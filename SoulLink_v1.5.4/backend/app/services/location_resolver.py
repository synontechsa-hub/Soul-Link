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
from backend.app.models.relationship import SoulRelationship
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
        
        # Priority 1: User-specific manual override
        if user_id:
            rel_result = await session.execute(
                select(SoulRelationship).where(
                    SoulRelationship.user_id == user_id,
                    SoulRelationship.soul_id == soul_id
                )
            )
            rel = rel_result.scalars().first()
            
            if rel and rel.current_location:
                return rel.current_location
        
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
        Efficiently resolves locations for multiple souls.
        Used by TimeManager for world state caching.
        
        Args:
            soul_ids: List of souls to locate
            time_slot: Current time slot
            session: Database session
        
        Returns:
            dict mapping soul_id -> location_id
        """
        locations = {}
        
        for soul_id in soul_ids:
            location = await LocationResolver.resolve_location(
                soul_id=soul_id,
                time_slot=time_slot,
                session=session,
                user_id=None  # Global context, no user overrides
            )
            locations[soul_id] = location
        
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
            await session.commit()
