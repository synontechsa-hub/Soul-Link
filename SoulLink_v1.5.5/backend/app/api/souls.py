import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select, col
from backend.app.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.soul import Soul, SoulPillar, SoulState
from backend.app.models.user import User
from backend.app.models.relationship import SoulRelationship
from backend.app.api.dependencies import get_current_user
from backend.app.core.rate_limiter import limiter, RateLimits
from typing import Optional

router = APIRouter(prefix="/souls", tags=["Legion Engine - Souls"])
logger = logging.getLogger("LegionEngine")

@router.get("/explore")
@limiter.limit(RateLimits.SOULS)
async def explore_souls(
    q: Optional[str] = None, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    try:
        # 1. Get existing links
        rel_result = await db.execute(
            select(SoulRelationship).where(SoulRelationship.user_id == user.user_id)
        )
        relationships = rel_result.scalars().all()
        linked_dict = {rel.soul_id: rel for rel in relationships}

        # 2. Get all souls and their live states
        soul_result = await db.execute(select(Soul))
        all_souls = soul_result.scalars().all()
        
        output = []
        for s in all_souls:
            rel = linked_dict.get(s.soul_id)
            state = await db.get(SoulState, s.soul_id)
            
            soul_data = {
                "id": s.soul_id,
                "name": s.name,
                "summary": s.summary[:100] + "..." if len(s.summary) > 100 else s.summary,
                "archetype": s.archetype or "Unknown",
                "is_linked": rel is not None,
                "portrait_url": s.portrait_url,
            }
            
            if rel:
                soul_data["intimacy_tier"] = rel.intimacy_tier
                soul_data["current_location"] = state.current_location_id if state else rel.current_location
            
            output.append(soul_data)
        
        return output
        
    except Exception as e:
        logger.error(f"Explore Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to scout for souls.")

@router.get("/{soul_id}")
async def get_soul_details(soul_id: str, db: AsyncSession = Depends(get_async_session)):
    """Get detailed public profile info aggregated from pillars."""
    soul = await db.get(Soul, soul_id)
    pillar = await db.get(SoulPillar, soul_id)
    
    if not soul or not pillar:
        raise HTTPException(404, detail=f"Soul {soul_id} not fully initialized.")
    
    return {
        "id": soul.soul_id,
        "name": soul.name,
        "summary": soul.summary,
        "archetype": soul.archetype,
        "portrait_url": soul.portrait_url,
        "appearance": pillar.aesthetic_pillar.get("description", ""),
        "voice_style": pillar.aesthetic_pillar.get("voice_style", ""),
        "signature_emote": pillar.aesthetic_pillar.get("signature_emote", "")
    }

@router.post("/{soul_id}/link")
@limiter.limit(RateLimits.USER_WRITE)
async def link_with_soul(
    soul_id: str,
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    """Initialize a relationship and establish the initial state."""
    soul = await session.get(Soul, soul_id)
    pillar = await session.get(SoulPillar, soul_id)
    state = await session.get(SoulState, soul_id)

    if not soul or not pillar or not state:
        raise HTTPException(404, detail=f"Soul {soul_id} definition incomplete.")
    
    rel_result = await session.execute(
        select(SoulRelationship).where(
            SoulRelationship.user_id == user.user_id,
            SoulRelationship.soul_id == soul_id
        )
    )
    existing = rel_result.scalars().first()
    
    if existing:
        return {
            "status": "already_linked",
            "soul_id": soul_id,
            "soul_name": soul.name,
            "intimacy_tier": existing.intimacy_tier
        }
    
    # Establish link at soul's current global position
    start_loc = state.current_location_id

    new_rel = SoulRelationship(
        user_id=user.user_id,
        soul_id=soul_id,
        intimacy_score=0,
        intimacy_tier="STRANGER",
        current_location=start_loc
    )
    
    # Architect recognition from Pillar meta
    dev_cfg = pillar.meta_data.get("dev_config", {})
    allowed_ids = dev_cfg.get("architect_ids", [])
    
    if user.user_id in allowed_ids:
        new_rel.is_architect = True
        new_rel.nsfw_unlocked = True 
    
    session.add(new_rel)
    await session.commit()
    await session.refresh(new_rel)
    
    return {
        "status": "linked",
        "soul_id": soul_id,
        "soul_name": soul.name,
        "location": start_loc,
        "message": f"Link established at {start_loc}."
    }

@router.get("/{soul_id}/relationship")
async def get_relationship_status(
    soul_id: str,
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session)
):
    """Check relationship status with synced state."""
    rel_result = await session.execute(
        select(SoulRelationship).where(
            SoulRelationship.user_id == user.user_id,
            SoulRelationship.soul_id == soul_id
        )
    )
    rel = rel_result.scalars().first()
    state = await session.get(SoulState, soul_id)
    
    if not rel:
        raise HTTPException(404, detail=f"No relationship with {soul_id}.")
    
    return {
        "soul_id": soul_id,
        "intimacy_score": rel.intimacy_score,
        "intimacy_tier": rel.intimacy_tier,
        "current_location": state.current_location_id if state else rel.current_location,
        "is_architect": rel.is_architect,
        "nsfw_unlocked": rel.nsfw_unlocked,
        "energy": state.energy if state else 100
    }
