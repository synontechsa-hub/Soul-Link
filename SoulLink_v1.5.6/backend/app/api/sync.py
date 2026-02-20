# /backend/app/api/sync.py
# /version.py v1.5.6 Normandy SR-2

import logging
from fastapi import APIRouter, Depends
from sqlmodel import select
from backend.app.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.dependencies import get_current_user
from backend.app.models.link_state import LinkState
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
        select(LinkState, Soul)
        .select_from(LinkState)
        .join(Soul, LinkState.soul_id == Soul.soul_id) 
        .where(LinkState.user_id == user.user_id)
    )
    res = await session.execute(statement)
    results = res.all()
    
    from backend.app.logic.time_manager import TimeManager
    from backend.app.models.time_slot import TimeSlot
    
    time_manager = TimeManager(session)
    # We need the user's current time slot to calculate where souls are
    current_slot = TimeSlot(user.current_time_slot)

    ARCHITECT_UUID = "14dd612d-744e-487d-b2d5-cc47732183d3"
    is_global_architect = user.user_id == ARCHITECT_UUID

    soul_states = []
    
    if is_global_architect:
        # 👑 GOD MODE: Return all souls (except lore-architect) as if linked
        # Optimization: Batch fetch all souls and existing link records in one pass
        all_souls_stmt = select(Soul).where(Soul.soul_id != "the_architect_01")
        soul_res = await session.execute(all_souls_stmt)
        all_souls = soul_res.scalars().all()
        
        # Batch fetch existing links for this architect
        all_links_stmt = select(LinkState).where(LinkState.user_id == user.user_id)
        links_res = await session.execute(all_links_stmt)
        links_map = {l.soul_id: l for l in links_res.scalars().all()}
        
        for soul in all_souls:
            link = links_map.get(soul.soul_id)
            
            display_location = link.current_location if link else await time_manager.get_soul_location_at_time(soul.soul_id, current_slot)
            
            soul_states.append({
                "soul_id": soul.soul_id,
                "name": soul.name,
                "archetype": soul.archetype,
                "portrait_url": soul.portrait_url, 
                "tier": "SOUL_LINKED" if is_global_architect else (link.intimacy_tier if link else "STRANGER"),
                "location": display_location,
                "last_interaction": link.last_interaction.isoformat() if (link and link.last_interaction) else None,
                "is_architect": True,
                "nsfw_unlocked": True
            })
    else:
        # Standard User logic
        for link, soul in results:
            display_location = link.current_location
            if not display_location:
                display_location = await time_manager.get_soul_location_at_time(soul.soul_id, current_slot)
            
            soul_states.append({
                "soul_id": link.soul_id,
                "name": soul.name,
                "archetype": soul.archetype,
                "portrait_url": soul.portrait_url, 
                "tier": link.intimacy_tier,
                "location": display_location,
                "last_interaction": link.last_interaction.isoformat() if link.last_interaction else None,
                "is_architect": link.is_architect,
                "nsfw_unlocked": link.unlocked_nsfw
            })
        
    return {
        "user_id": user.user_id,
        "username": user.username,
        "display_name": user.display_name,
        "active_souls": soul_states,
        "total_links": len(soul_states)
    }