# /backend/app/api/sync.py
# /version.py v1.5.4 Arise

import logging
from fastapi import APIRouter, Depends
from sqlmodel import select
from backend.app.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.dependencies import get_current_user
from backend.app.models.relationship import SoulRelationship
from backend.app.models.soul import Soul
from backend.app.models.user import User

router = APIRouter(prefix="/sync", tags=["Legion Engine - Sync"])
logger = logging.getLogger("LegionEngine")

@router.get("/dashboard")
async def get_full_state(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    THE PULSE: Fetches world-state with portrait data.
    """
    statement = (
        select(SoulRelationship, Soul)
        .select_from(SoulRelationship)
        .join(Soul, SoulRelationship.soul_id == Soul.soul_id) 
        .where(SoulRelationship.user_id == user.user_id)
    )
    res = await session.execute(statement)
    results = res.all()
    
    from backend.app.logic.time_manager import TimeManager
    from backend.app.models.time_slot import TimeSlot
    
    time_manager = TimeManager(session)
    # We need the user's current time slot to calculate where souls are
    current_slot = TimeSlot(user.current_time_slot)

    soul_states = []
    for rel, soul in results:
        # 🔗 UNIFIED LOCATION RESOLUTION
        # Manual Override > Dynamic Routine
        display_location = rel.current_location
        if not display_location:
            display_location = await time_manager.get_soul_location_at_time(soul.soul_id, current_slot)
        
        soul_states.append({
            "soul_id": rel.soul_id,
            "name": soul.name,
            "archetype": soul.archetype,
            "portrait_url": soul.portrait_url, 
            "tier": rel.intimacy_tier,
            "location": display_location, # ✅ Unified!
            "last_interaction": rel.last_interaction.isoformat() if rel.last_interaction else None,
            "is_architect": rel.is_architect,
            "nsfw_unlocked": rel.nsfw_unlocked
        })
        
    return {
        "user_id": user.user_id,
        "username": user.username,
        "display_name": user.display_name,
        "active_souls": soul_states,
        "total_links": len(soul_states)
    }