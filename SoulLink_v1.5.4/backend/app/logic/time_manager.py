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
        Resolve where a soul is based on their routine pillar.
        """
        result = await self.session.execute(
            text("SELECT routines FROM soul_pillars WHERE soul_id = :soul_id"),
            {"soul_id": soul_id}
        )
        row = result.fetchone()
        
        if not row:
            # Fallback to current state if no pillar found
            state_result = await self.session.execute(
                text("SELECT current_location_id FROM soul_states WHERE soul_id = :soul_id"),
                {"soul_id": soul_id}
            )
            state_row = state_result.fetchone()
            return state_row[0] if state_row else "soul_plaza"
        
        import json
        routines_raw = row[0]
        routines = json.loads(routines_raw) if isinstance(routines_raw, str) else routines_raw
        
        if routines and time_slot.value in routines:
            return routines[time_slot.value]
        
        # Final fallback to live state
        state_result = await self.session.execute(
            text("SELECT current_location_id FROM soul_states WHERE soul_id = :soul_id"),
            {"soul_id": soul_id}
        )
        state_row = state_result.fetchone()
        return state_row[0] if state_row else "soul_plaza"
    
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
            text("SELECT soul_id, current_location_id FROM soul_states")
        )
        rows = souls_result.fetchall()
        
        soul_locations = {soul_id: loc for soul_id, loc in rows}
        
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
