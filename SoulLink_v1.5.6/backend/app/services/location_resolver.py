# /backend/app/services/location_resolver.py
# v1.5.5 - Single Source of Truth for Soul Locations

"""
LocationResolver Service
Implements the 4-tier priority hierarchy for soul location resolution.

Priority Order:
1. Manual Override (SoulRelationship.current_location) - User-specific
2. Time-Based Routine (SoulPillar.routines[time_slot]) - Scheduled
3. Global Live State (SoulState.current_location_id) - Real-time
4. Default Fallback ("soul_plaza") - Safety net
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from backend.app.models.soul import SoulPillar, SoulState
from backend.app.models.link_state import LinkState
from backend.app.models.time_slot import TimeSlot

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
        Resolves a soul's location using the 4-tier priority hierarchy.
        
        Args:
            soul_id: The soul to locate
            time_slot: Current time slot for routine resolution
            session: Database session
            user_id: Optional user context for manual overrides
        
        Returns:
            location_id (str): The resolved location
        """
        
        # Priority 1: User-specific manual override (LinkState)
        if user_id:
            from sqlalchemy import select
            link_result = await session.execute(
                select(LinkState).where(
                    LinkState.user_id == user_id,
                    LinkState.soul_id == soul_id
                )
            )
            link = link_result.scalars().first()
            
            if link and link.current_location:
                return link.current_location
        
        # Priority 2: Time-based routine from pillar
        pillar = await session.get(SoulPillar, soul_id)
        if pillar and pillar.routines:
            routine_loc = pillar.routines.get(time_slot.value)
            if routine_loc:
                return routine_loc
        
        # Priority 3: Global live state
        state = await session.get(SoulState, soul_id)
        if state and state.current_location_id:
            return state.current_location_id
        
        # Priority 4: Default fallback
        return "soul_plaza"
    
    @staticmethod
    async def resolve_bulk_locations(
        soul_ids: list[str],
        time_slot: TimeSlot,
        session: AsyncSession
    ) -> dict[str, str]:
        """
        Efficiently resolves locations for multiple souls using bulk queries.
        Used by TimeManager for world state caching.
        """
        from sqlmodel import select
        
        # Bulk fetch Pillars for Routines (Optimized: Lazy Load)
        from sqlalchemy.orm import load_only
        pillar_result = await session.execute(
            select(SoulPillar)
            .where(SoulPillar.soul_id.in_(soul_ids))
            .options(load_only(SoulPillar.soul_id, SoulPillar.routines))
        )
        pillar_map = {p.soul_id: p for p in pillar_result.scalars().all()}
        
        # Bulk fetch States for Global Live State
        state_result = await session.execute(
            select(SoulState).where(SoulState.soul_id.in_(soul_ids))
        )
        state_map = {s.soul_id: s for s in state_result.scalars().all()}
        
        locations = {}
        for soul_id in soul_ids:
            # Priority 2: Routine
            pillar = pillar_map.get(soul_id)
            if pillar and pillar.routines:
                routine_loc = pillar.routines.get(time_slot.value)
                if routine_loc:
                    locations[soul_id] = routine_loc
                    continue
            
            # Priority 3: Global State
            state = state_map.get(soul_id)
            if state and state.current_location_id:
                locations[soul_id] = state.current_location_id
                continue
            
            # Priority 4: Default
            locations[soul_id] = "soul_plaza"
            
        return locations
    
    @staticmethod
    async def update_global_location(
        soul_id: str,
        location_id: str,
        session: AsyncSession
    ) -> None:
        """
        Updates the global live state for a soul.
        Used by LocationManager when souls move.
        
        Args:
            soul_id: Soul to update
            location_id: New location
            session: Database session
        """
        from datetime import datetime
        
        state = await session.get(SoulState, soul_id)
        if state:
            state.current_location_id = location_id
            state.last_updated = datetime.utcnow()
            session.add(state)
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                # Log error but don't raise - this is a background update
                print(f"⚠️ Failed to update global location for {soul_id}: {e}")


    @staticmethod
    async def get_all_locations(session: AsyncSession) -> list:
        """Returns all locations from the database."""
        from backend.app.models.location import Location
        result = await session.execute(select(Location))
        return result.scalars().all()
