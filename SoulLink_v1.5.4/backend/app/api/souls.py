# /backend/app/api/souls.py
# version.py
# _dev/

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, col
from backend.app.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.soul import Soul
from backend.app.models.user import User
from backend.app.models.relationship import SoulRelationship
from backend.app.api.dependencies import get_current_user 
from typing import Optional # Ensure this is imported

router = APIRouter(prefix="/souls", tags=["Legion Engine - Souls"])
logger = logging.getLogger("LegionEngine")

@router.get("/explore")
async def explore_souls(
    q: Optional[str] = None, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_async_session)
):
    try:
        # 1. Get existing links
        linked_statement = select(SoulRelationship).where(
            SoulRelationship.user_id == user.user_id
        )
        rel_result = await db.execute(linked_statement)
        relationships = rel_result.scalars().all()
        linked_dict = {rel.soul_id: rel for rel in relationships}

        # 2. Search Query
        statement = select(Soul)
        
        soul_result = await db.execute(statement)
        all_souls = soul_result.scalars().all()
        
        output = []
        for s in all_souls:
            rel = linked_dict.get(s.soul_id)
            
            soul_data = {
                "id": s.soul_id,
                "name": s.name,
                "tagline": s.summary[:100] + "..." if len(s.summary) > 100 else s.summary,
                "archetype": s.archetype or "Unknown",
                "is_linked": rel is not None,
                # ✅ FIX: Read directly from the DB source of truth
                "portrait_url": s.portrait_url or s.meta.get("portrait_full") or f"/assets/images/souls/{s.soul_id}_01.jpeg",
            }
            
            if rel:
                soul_data["intimacy_tier"] = rel.intimacy_tier
                soul_data["current_location"] = rel.current_location
            
            output.append(soul_data)
        
        return output
        
    except Exception as e:
        logger.error(f"Phoenix Explore Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to scout for souls.")

@router.get("/{soul_id}")
async def get_soul_details(soul_id: str, db: AsyncSession = Depends(get_async_session)):
    """Get detailed public profile info."""
    soul = await db.get(Soul, soul_id)
    if not soul:
        raise HTTPException(404, detail=f"Soul {soul_id} not found.")
    
    return {
        "id": soul.soul_id,
        "name": soul.name,
        "summary": soul.summary,
        "archetype": soul.archetype,
        "portrait_url": soul.portrait_url, # ✅ Sending the face
        "home_base": soul.home_base,       # ✅ Sending the home district
        "appearance": soul.aesthetic_pillar.get("description", ""),
        "voice_style": soul.aesthetic_pillar.get("voice_style", ""),
        "signature_emote": soul.aesthetic_pillar.get("signature_emote", "")
    }

@router.post("/{soul_id}/link")
async def link_with_soul(
    soul_id: str,
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session)
):
    """Initialize a relationship with a soul."""
    soul = await session.get(Soul, soul_id)
    if not soul:
        raise HTTPException(404, detail=f"Soul {soul_id} not found.")
    
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
    
    # ✅ FIX: Use the Soul's specific spawn point (e.g. Stop n Go)
    # If spawn_location is missing, fallback to 'soul_plaza'
    start_loc = soul.spawn_location if soul.spawn_location else "soul_plaza"

    new_rel = SoulRelationship(
        user_id=user.user_id,
        soul_id=soul_id,
        intimacy_score=0,
        intimacy_tier="STRANGER",
        current_location=None # <--- Follows Dynamic Routine
    )
    
    # 🕵️ ARCHITECT RECOGNITION (Blueprint Allowlist)
    dev_cfg = soul.meta_data.get("dev_config", {})
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

# ... (get_relationship_status remains the same)

@router.get("/{soul_id}/relationship")
async def get_relationship_status(
    soul_id: str,
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session)
):
    """Check your current relationship status with a soul."""
    rel_result = await session.execute(
        select(SoulRelationship).where(
            SoulRelationship.user_id == user.user_id,
            SoulRelationship.soul_id == soul_id
        )
    )
    rel = rel_result.scalars().first()
    
    if not rel:
        raise HTTPException(404, detail=f"No relationship with {soul_id}.")
    
    return {
        "soul_id": soul_id,
        "intimacy_score": rel.intimacy_score,
        "intimacy_tier": rel.intimacy_tier,
        "current_location": rel.current_location,
        "is_architect": rel.is_architect,
        "nsfw_unlocked": rel.nsfw_unlocked
    }
