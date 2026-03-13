# /backend/app/services/location_resolver.py
# v1.5.6 Normandy SR-2 — Production hardened
# _dev/ dependency removed. Routines loaded from DB at startup.

"""
LocationResolver Service
Implements the 4-tier priority hierarchy for soul location resolution.

Priority Order:
1. Manual Override (LinkState.current_location) - User-specific
2. Routine v2 (SoulPillar.routine) - Template-based via DB cache
3. Legacy Routine (SoulPillar.routines) - Pre-populated fallback
4. Global Live State (SoulState.current_location_id)
5. Default Fallback ("soul_plaza")
"""

import logging
from typing import Optional
from datetime import datetime, timezone
from backend.app.core.utils import utcnow
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from backend.app.models.soul import SoulPillar, SoulState
from backend.app.models.link_state import LinkState
from backend.app.models.time_slot import TimeSlot

logger = logging.getLogger("LocationResolver")

# ── Module-level routines cache ─────────────────────────────────────────────
# Populated once at startup by main.py via initialize_routines_cache().
# Never read from disk after boot.
_ROUTINES_CACHE: dict = {}


def initialize_routines_cache(data: dict) -> None:
    """
    Called once at startup after system_config is loaded from DB.
    Populates the in-memory routines template cache.
    """
    global _ROUTINES_CACHE
    _ROUTINES_CACHE = data
    logger.info(f"Routines cache loaded: {len(data)} templates")


class LocationResolver:
    """
    Single source of truth for soul location resolution.
    Ensures consistent location queries across the entire application.
    """

    @staticmethod
    async def resolve_location(
        soul_id: str,
        time_slot: TimeSlot,
        session: AsyncSession,
        user_id: Optional[str] = None
    ) -> str:
        """
        Resolves a soul's location using the v1.5.6 priority hierarchy.
        Uses in-memory routines cache — no disk reads.
        """

        # Priority 1: User-specific manual override (LinkState)
        if user_id:
            link_result = await session.execute(
                select(LinkState).where(
                    LinkState.user_id == user_id,
                    LinkState.soul_id == soul_id
                )
            )
            link = link_result.scalars().first()
            if link and link.current_location:
                return link.current_location

        # Priority 2: Routine v2 / Logic Pillar (DB cache)
        pillar = await session.get(SoulPillar, soul_id)
        if pillar and pillar.routine:
            is_weekend = utcnow().weekday() >= 5
            day_type = "weekend" if is_weekend else "weekday"

            # Check schedule overrides first
            overrides = pillar.routine.get("schedule_overrides", {})
            day_overrides = overrides.get(day_type, {})
            if time_slot.value in day_overrides:
                target_zone = day_overrides[time_slot.value]
                if "_" in target_zone or target_zone == "soul_plaza":
                    return target_zone
                pref = pillar.routine.get(
                    "location_preferences", {}).get(target_zone)
                if pref:
                    return pref

            # Check template from in-memory cache (no file reads)
            template_id = pillar.routine.get("template_id")
            if template_id and _ROUTINES_CACHE:
                tmpl = _ROUTINES_CACHE.get(template_id, {})
                zone_key = tmpl.get("schedule", {}).get(
                    day_type, {}).get(time_slot.value)
                if zone_key:
                    loc_id = pillar.routine.get(
                        "location_preferences", {}).get(zone_key)
                    if loc_id:
                        return loc_id

        # Priority 3: Legacy pre-populated routines map
        if pillar and pillar.routines:
            routine_loc = pillar.routines.get(time_slot.value)
            if routine_loc:
                return routine_loc

        # Priority 4: Global live state
        state = await session.get(SoulState, soul_id)
        if state and state.current_location_id:
            return state.current_location_id

        # Priority 5: Default fallback
        return "soul_plaza"

    @staticmethod
    async def resolve_bulk_locations(
        soul_ids: list[str],
        time_slot: TimeSlot,
        session: AsyncSession
    ) -> dict[str, str]:
        """
        Efficiently resolves locations for multiple souls using bulk queries.
        Uses in-memory routines cache — no file reads inside the loop.
        """
        from sqlalchemy.orm import load_only

        is_weekend = utcnow().weekday() >= 5
        day_type = "weekend" if is_weekend else "weekday"

        # Bulk fetch Pillars
        pillar_result = await session.execute(
            select(SoulPillar)
            .where(SoulPillar.soul_id.in_(soul_ids))
        )
        pillar_map = {p.soul_id: p for p in pillar_result.scalars().all()}

        # Bulk fetch States
        state_result = await session.execute(
            select(SoulState).where(SoulState.soul_id.in_(soul_ids))
        )
        state_map = {s.soul_id: s for s in state_result.scalars().all()}

        locations = {}
        for soul_id in soul_ids:
            pillar = pillar_map.get(soul_id)
            resolved = False

            if pillar and pillar.routine:
                routine_data = pillar.routine

                # Check schedule overrides
                overrides = routine_data.get("schedule_overrides", {})
                day_overrides = overrides.get(day_type, {})
                if time_slot.value in day_overrides:
                    target_zone = day_overrides[time_slot.value]
                    pref = routine_data.get("location_preferences", {}).get(
                        target_zone, target_zone)
                    if pref:
                        locations[soul_id] = pref
                        resolved = True

                # Fall back to template from cache
                if not resolved and _ROUTINES_CACHE:
                    template_id = routine_data.get("template_id")
                    if template_id:
                        tmpl = _ROUTINES_CACHE.get(template_id, {})
                        zone_key = tmpl.get("schedule", {}).get(
                            day_type, {}).get(time_slot.value)
                        if zone_key:
                            loc_id = routine_data.get(
                                "location_preferences", {}).get(zone_key)
                            if loc_id:
                                locations[soul_id] = loc_id
                                resolved = True

            # Legacy pre-populated routines map
            if not resolved and pillar and pillar.routines:
                routine_loc = pillar.routines.get(time_slot.value)
                if routine_loc:
                    locations[soul_id] = routine_loc
                    resolved = True

            # Global live state
            if not resolved:
                state = state_map.get(soul_id)
                if state and state.current_location_id:
                    locations[soul_id] = state.current_location_id
                    resolved = True

            if not resolved:
                locations[soul_id] = "soul_plaza"

        return locations

    @staticmethod
    async def update_global_location(
        soul_id: str,
        location_id: str,
        session: AsyncSession
    ) -> None:
        """Updates the global live state for a soul."""
        state = await session.get(SoulState, soul_id)
        if state:
            state.current_location_id = location_id
            state.last_updated = utcnow()
            session.add(state)
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.warning(
                    f"Failed to update global location for {soul_id}: {e}")

    @staticmethod
    async def get_all_locations(session: AsyncSession) -> list:
        """Returns all locations from the database."""
        from backend.app.models.location import Location
        result = await session.execute(select(Location))
        return list(result.scalars().all())
