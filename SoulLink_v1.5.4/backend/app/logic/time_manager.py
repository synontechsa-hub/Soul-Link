# /backend/app/logic/time_manager.py
# /version.py v1.5.4 Arise
# /_dev/

# "Time is a flat circle."
# - Rust Cohle, True Detective

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.cache import cache_service
from backend.app.models.time_slot import TimeSlot, get_next_time_slot
from typing import Optional, Dict, List

class TimeManager:
    """
    Manages time slot progression and soul routine resolution.
    The silent orchestrator of Link City's daily rhythm.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def advance_time_slot(self, user_id: str, target_slot: Optional[TimeSlot] = None) -> TimeSlot:
        """
        Advance user's time slot and potentially resolve world state movement.
        """
        # Get current time slot
        result = await self.session.execute(
            text("SELECT current_time_slot FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        row = result.fetchone()
        
        if not row:
            raise ValueError(f"User {user_id} not found")
        
        current_slot = TimeSlot(row[0])
        new_slot = target_slot if target_slot else get_next_time_slot(current_slot)
        
        # Update user's time slot
        await self.session.execute(
            text("UPDATE users SET current_time_slot = :new_slot WHERE user_id = :user_id"),
            {"new_slot": new_slot.value, "user_id": user_id}
        )
        
        # TODO: Trigger soul movement resolution based on routines here if needed
        # For now, we trust the manual movement or the routine retrieval during lookups.
        
        await self.session.commit()
        return new_slot
    
    async def get_soul_location_at_time(self, soul_id: str, time_slot: TimeSlot) -> str:
        """
        Resolve where a soul is at a specific time using LocationResolver.
        """
        from backend.app.services.location_resolver import LocationResolver
        
        return await LocationResolver.resolve_location(
            soul_id=soul_id,
            time_slot=time_slot,
            session=self.session,
            user_id=None  # Global context
        )
    
    async def get_world_state(self, user_id: str) -> Dict:
        """
        Get the complete world state for a user at their current time slot.
        """
        user_result = await self.session.execute(
            text("SELECT current_time_slot FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        user_row = user_result.fetchone()
        
        if not user_row:
            raise ValueError(f"User {user_id} not found")
        
        current_slot = TimeSlot(user_row[0])
        cache_key = f"world:state:{current_slot.value}"
        
        # Check cache
        cached_data = cache_service.get(cache_key)
        if cached_data:
            return {
                "time_slot": current_slot.value,
                "soul_locations": cached_data
            }
        
        # Fetch all live locations from soul_states
        souls_result = await self.session.execute(
            text("SELECT soul_id FROM souls")
        )
        soul_ids = [row[0] for row in souls_result.fetchall()]
        
        # Resolve locations using LocationResolver (includes routines!)
        from backend.app.services.location_resolver import LocationResolver
        soul_locations = await LocationResolver.resolve_bulk_locations(
            soul_ids=soul_ids,
            time_slot=current_slot,
            session=self.session
        )
        
        # Update cache (5 minute TTL)
        cache_service.set(cache_key, soul_locations, ttl=300)

        return {
            "time_slot": current_slot.value,
            "soul_locations": soul_locations
        }
    
    async def get_souls_at_location(self, user_id: str, location_id: str) -> List[str]:
        """Get all souls present at a specific location."""
        world_state = await self.get_world_state(user_id)
        return [
            soul_id for soul_id, loc in world_state["soul_locations"].items()
            if loc == location_id
        ]
