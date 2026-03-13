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
from backend.app.core.config import settings

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

    is_global_architect = user.user_id == settings.architect_uuid

    soul_states = []

    if is_global_architect:
        # 👑 GOD MODE: Return all souls (except lore-architect) as if linked
        all_souls_stmt = select(Soul).where(Soul.soul_id != "the_architect_01")
        soul_res = await session.execute(all_souls_stmt)
        all_souls = soul_res.scalars().all()

        # Batch fetch existing links for this architect
        all_links_stmt = select(LinkState).where(
            LinkState.user_id == user.user_id)
        links_res = await session.execute(all_links_stmt)
        links_map = {l.soul_id: l for l in links_res.scalars().all()}

        # ── BULK LOCATION RESOLVE — no N+1 ───────────────────────────────────
        # Only resolve souls that don't have a link override
        needs_resolve = [s.soul_id for s in all_souls
                         if not (links_map.get(s.soul_id) and links_map[s.soul_id].current_location)]
        from backend.app.services.location_resolver import LocationResolver
        bulk_locations = await LocationResolver.resolve_bulk_locations(
            soul_ids=needs_resolve,
            time_slot=current_slot,
            session=session
        )

        for soul in all_souls:
            link = links_map.get(soul.soul_id)
            display_location = (link.current_location if link and link.current_location
                                else bulk_locations.get(soul.soul_id, "soul_plaza"))

            soul_states.append({
                "soul_id": soul.soul_id,
                "name": soul.name,
                "archetype": soul.archetype,
                "portrait_url": soul.portrait_url,
                "tier": "SOUL_LINKED",
                "location": display_location,
                "last_interaction": link.last_interaction.isoformat() if (link and link.last_interaction) else None,
                "is_architect": True,
                "nsfw_unlocked": True
            })
    else:
        # Standard User logic
        # ── BULK LOCATION RESOLVE — no N+1 ───────────────────────────────────
        needs_resolve = [link.soul_id for link, _ in results if not link.current_location]
        from backend.app.services.location_resolver import LocationResolver
        bulk_locations = await LocationResolver.resolve_bulk_locations(
            soul_ids=needs_resolve,
            time_slot=current_slot,
            session=session
        )

        for link, soul in results:
            display_location = link.current_location
            if not display_location:
                display_location = bulk_locations.get(soul.soul_id, "soul_plaza")

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
