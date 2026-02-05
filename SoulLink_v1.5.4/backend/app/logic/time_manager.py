# /backend/app/logic/time_manager.py
# /version.py v1.5.4 Arise
# /_dev/

# "Time is a flat circle."
# - Rust Cohle, True Detective

import threading
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.time_slot import TimeSlot, get_next_time_slot
from typing import Optional, Dict, List

class TimeManager:
    """
    Manages time slot progression and soul routine resolution.
    The silent orchestrator of Link City's daily rhythm.
    """
    _world_state_cache: Dict[str, Dict[str, str]] = {}
    _cache_lock = threading.Lock()
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def advance_time_slot(self, user_id: str, target_slot: Optional[TimeSlot] = None) -> TimeSlot:
        """
        Advance user's time slot asynchronously.
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
        
        # Determine new slot
        if target_slot:
            new_slot = target_slot
        else:
            new_slot = get_next_time_slot(current_slot)
        
        # Update user's time slot
        await self.session.execute(
            text("UPDATE users SET current_time_slot = :new_slot WHERE user_id = :user_id"),
            {"new_slot": new_slot.value, "user_id": user_id}
        )
        await self.session.commit()
        
        return new_slot
    
    async def get_soul_location_at_time(self, soul_id: str, time_slot: TimeSlot) -> str:
        """
        Resolve where a soul is during a specific time slot asynchronously.
        """
        result = await self.session.execute(
            text("SELECT routines, spawn_location FROM souls WHERE soul_id = :soul_id"),
            {"soul_id": soul_id}
        )
        row = result.fetchone()
        
        if not row:
            return "soul_plaza"  # Default fallback
        
        import json
        routines_raw, spawn_location = row
        routines = json.loads(routines_raw) if isinstance(routines_raw, str) else routines_raw
        
        if routines and time_slot.value in routines:
            return routines[time_slot.value]
        
        return spawn_location or "soul_plaza"
    
    async def get_world_state(self, user_id: str) -> Dict:
        """
        Get the complete world state for a user's current time slot asynchronously.
        """
        user_result = await self.session.execute(
            text("SELECT current_time_slot FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        user_row = user_result.fetchone()
        
        if not user_row:
            raise ValueError(f"User {user_id} not found")
        
        current_slot = TimeSlot(user_row[0])
        
        # --- CACHE LOOKUP ---
        # Note: Cache is shared across instances, but lock is local.
        # For a truly distributed system, we'd use Redis.
        if current_slot.value in self._world_state_cache:
            return {
                "time_slot": current_slot.value,
                "soul_locations": self._world_state_cache[current_slot.value]
            }
        
        souls_result = await self.session.execute(
            text("SELECT soul_id, routines, spawn_location FROM souls")
        )
        rows = souls_result.fetchall()
        
        import json
        soul_locations = {}
        for soul_id, routines_raw, spawn_location in rows:
            routines = json.loads(routines_raw) if isinstance(routines_raw, str) else routines_raw
            if routines and current_slot.value in routines:
                soul_locations[soul_id] = routines[current_slot.value]
            else:
                soul_locations[soul_id] = spawn_location or "soul_plaza"
        
        # Update cache
        self._world_state_cache[current_slot.value] = soul_locations

        return {
            "time_slot": current_slot.value,
            "soul_locations": soul_locations
        }
    
    async def get_souls_at_location(self, user_id: str, location_id: str) -> List[str]:
        """
        Get all souls present at a specific location asynchronously.
        """
        world_state = await self.get_world_state(user_id)
        souls_here = [
            soul_id for soul_id, loc in world_state["soul_locations"].items()
            if loc == location_id
        ]
        return souls_here
