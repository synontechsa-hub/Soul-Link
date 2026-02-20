# /backend/app/api/souls.py
# v1.5.6 Normandy SR-2 — Soul Discovery & Linking
# UPDATED: Link endpoint now creates LinkState (not SoulRelationship).
#          Relationship status reads from LinkState.

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select, col
from backend.app.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.soul import Soul, SoulPillar, SoulState
from backend.app.models.user import User
from backend.app.models.link_state import LinkState
from backend.app.models.soul_memory import SoulMemory
from backend.app.api.dependencies import get_current_user
from backend.app.core.rate_limiter import limiter, RateLimits
from backend.app.core.cache import cache_service
from typing import Optional

router = APIRouter(prefix="/souls", tags=["Legion Engine - Souls"])
logger = logging.getLogger("LegionEngine")


# ==========================================
# HELPERS
# ==========================================

async def _get_soul_blueprint(soul_id: str, session: AsyncSession):
    """
    Fetch Soul + SoulPillar with caching.
    Cache key: soul:blueprint:{soul_id} (TTL: 1 hour)
    """
    cache_key = f"soul:blueprint:{soul_id}"
    cached = cache_service.get(cache_key)
    if cached:
        return cached.get("soul"), cached.get("pillar")

    soul = await session.get(Soul, soul_id)
    pillar = await session.get(SoulPillar, soul_id)

    if soul and pillar:
        cache_service.set(cache_key, {
            "soul": soul,
            "pillar": pillar
        }, ttl=3600)  # 1 hour — blueprints are immutable

    return soul, pillar


# ==========================================
# ENDPOINTS
# ==========================================

@router.get("/explore")
@limiter.limit(RateLimits.SOULS)
async def explore_souls(
    q: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    """Discover available souls and see which ones you're linked with."""
    try:
        # 1. Get existing LinkStates for this user
        link_result = await db.execute(
            select(LinkState).where(LinkState.user_id == user.user_id)
        )
        links = link_result.scalars().all()
        linked_dict = {link.soul_id: link for link in links}

        # 2. Get all souls
        soul_result = await db.execute(select(Soul))
        all_souls = soul_result.scalars().all()

        # 3. Batch fetch SoulStates (Fix N+1)
        soul_ids = [s.soul_id for s in all_souls]
        state_result = await db.execute(select(SoulState).where(SoulState.soul_id.in_(soul_ids)))
        state_map = {state.soul_id: state for state in state_result.scalars().all()}

        output = []
        for s in all_souls:
            link = linked_dict.get(s.soul_id)
            state = state_map.get(s.soul_id)

            soul_data = {
                "id": s.soul_id,
                "name": s.name,
                "summary": s.summary[:100] + "..." if len(s.summary) > 100 else s.summary,
                "archetype": s.archetype or "Unknown",
                "is_linked": link is not None,
                "portrait_url": s.portrait_url,
            }

            if link:
                soul_data["intimacy_tier"] = link.intimacy_tier
                soul_data["signal_stability"] = link.signal_stability
                soul_data["current_location"] = link.current_location or (
                    state.current_location_id if state else "Unknown"
                )

            output.append(soul_data)

        return output

    except Exception as e:
        logger.error(f"Explore Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to scout for souls.")


@router.get("/{soul_id}")
async def get_soul_details(soul_id: str, db: AsyncSession = Depends(get_async_session)):
    """Get detailed public profile info aggregated from pillars."""
    soul, pillar = await _get_soul_blueprint(soul_id, db)

    if not soul or not pillar:
        raise HTTPException(404, detail=f"Soul {soul_id} not fully initialized.")

    aesthetic = pillar.aesthetic or {}
    speech = aesthetic.get("speech_profile", {})
    return {
        "id": soul.soul_id,
        "name": soul.name,
        "summary": soul.summary,
        "archetype": soul.archetype,
        "portrait_url": soul.portrait_url,
        "appearance": aesthetic.get("description", ""),
        "voice_style": speech.get("voice_style", ""),
        "signature_emote": speech.get("signature_emote", "")
    }



@router.post("/{soul_id}/link")
@limiter.limit(RateLimits.USER_WRITE)
async def link_with_soul(
    soul_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    """
    Initialize a LinkState between the user and a soul.
    This is the single source of truth for the user-soul relationship.
    """
    soul, pillar = await _get_soul_blueprint(soul_id, session)
    state = await session.get(SoulState, soul_id)

    if not soul or not pillar or not state:
        raise HTTPException(404, detail=f"Soul {soul_id} definition incomplete.")

    # Check if already linked
    existing_result = await session.execute(
        select(LinkState).where(
            LinkState.user_id == user.user_id,
            LinkState.soul_id == soul_id
        )
    )
    existing = existing_result.scalars().first()

    if existing:
        return {
            "status": "already_linked",
            "soul_id": soul_id,
            "soul_name": soul.name,
            "intimacy_tier": existing.intimacy_tier,
            "signal_stability": existing.signal_stability
        }

    # Determine architect status from pillar dev_config
    dev_cfg = pillar.meta_data.get("dev_config", {}) if pillar.meta_data else {}
    allowed_ids = dev_cfg.get("architect_ids", [])
    is_architect = user.user_id in allowed_ids

    # Create the LinkState (single source of truth)
    new_link = LinkState(
        user_id=user.user_id,
        soul_id=soul_id,
        current_location=state.current_location_id,
        intimacy_score=0,
        intimacy_tier="STRANGER",
        signal_stability=100.0,
        is_architect=is_architect,
        unlocked_nsfw=is_architect  # Architects get NSFW unlocked by default
    )
    session.add(new_link)
    await session.commit()
    await session.refresh(new_link)

    logger.info(f"Link established: user={user.user_id} soul={soul_id} architect={is_architect}")

    return {
        "status": "linked",
        "soul_id": soul_id,
        "soul_name": soul.name,
        "location": state.current_location_id,
        "is_architect": is_architect,
        "message": f"Link established at {state.current_location_id}."
    }


@router.get("/{soul_id}/relationship")
async def get_relationship_status(
    soul_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Check relationship status — reads from LinkState."""
    link_result = await session.execute(
        select(LinkState).where(
            LinkState.user_id == user.user_id,
            LinkState.soul_id == soul_id
        )
    )
    link = link_result.scalars().first()

    if not link:
        raise HTTPException(404, detail=f"No link with soul '{soul_id}'. Link with this soul first.")

    state = await session.get(SoulState, soul_id)

    return {
        "soul_id": soul_id,
        "intimacy_score": link.intimacy_score,
        "intimacy_tier": link.intimacy_tier,
        "signal_stability": link.signal_stability,
        "mask_integrity": link.mask_integrity,
        "current_location": link.current_location or (state.current_location_id if state else "Unknown"),
        "current_mood": link.current_mood,
        "is_architect": link.is_architect,
        "nsfw_unlocked": link.unlocked_nsfw,
        "total_messages_sent": link.total_messages_sent,
        "flags": link.flags
    }


@router.get("/{soul_id}/memories")
async def get_soul_memories(
    soul_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Fetch the narrative memory (The Notebook) for a user-soul pair.
    Used by the Apartment Memory Wall.
    """
    # Find the LinkState first
    link_result = await session.execute(
        select(LinkState).where(
            LinkState.user_id == user.user_id,
            LinkState.soul_id == soul_id
        )
    )
    link = link_result.scalars().first()

    if not link:
        raise HTTPException(404, detail=f"No link with soul '{soul_id}'.")

    # Fetch memory
    memory_result = await session.execute(
        select(SoulMemory).where(SoulMemory.link_state_id == link.id)
    )
    memory = memory_result.scalars().first()

    if not memory:
        return {
            "soul_id": soul_id,
            "summary": "No memories yet. Start a conversation.",
            "facts": {},
            "milestones": [],
            "total_messages": link.total_messages_sent
        }

    return {
        "soul_id": soul_id,
        "summary": memory.summary,
        "facts": memory.facts,
        "milestones": memory.milestones,
        "last_updated": memory.last_updated.isoformat(),
        "total_messages": link.total_messages_sent
    }
