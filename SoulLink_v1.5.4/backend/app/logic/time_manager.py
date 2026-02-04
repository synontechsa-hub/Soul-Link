# /backend/app/logic/time_manager.py
# /version.py v1.5.4 Arise
# /_dev/

# "Time is a flat circle."
# - Rust Cohle, True Detective

import threading
from sqlalchemy import Engine, text
from backend.app.models.time_slot import TimeSlot, get_next_time_slot
from typing import Optional, Dict, List

class TimeManager:
    """
    Manages time slot progression and soul routine resolution.
    The silent orchestrator of Link City's daily rhythm.
    """
    _world_state_cache: Dict[str, Dict[str, str]] = {}
    _cache_lock = threading.Lock()
    
    def __init__(self, engine: Engine):
        self.engine = engine
    
    def advance_time_slot(self, user_id: str, target_slot: Optional[TimeSlot] = None) -> TimeSlot:
        """
        Advance user's time slot to the next one (or jump to a specific slot).
        
        Args:
            user_id: The user's UUID
            target_slot: Optional specific time slot to jump to. If None, advances to next.
        
        Returns:
            The new time slot
        """
        with self.engine.connect() as conn:
            # Get current time slot
            result = conn.execute(
                text("SELECT current_time_slot FROM users WHERE user_id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            
            if not result:
                raise ValueError(f"User {user_id} not found")
            
            current_slot = TimeSlot(result[0])
            
            # Determine new slot
            if target_slot:
                new_slot = target_slot
            else:
                new_slot = get_next_time_slot(current_slot)
            
            # Update user's time slot
            conn.execute(
                text("UPDATE users SET current_time_slot = :new_slot WHERE user_id = :user_id"),
                {"new_slot": new_slot.value, "user_id": user_id}
            )
            conn.commit()
            
            return new_slot
    
    def get_soul_location_at_time(self, soul_id: str, time_slot: TimeSlot) -> str:
        """
        Resolve where a soul is during a specific time slot.
        
        Args:
            soul_id: The soul's ID
            time_slot: The time slot to check
        
        Returns:
            location_id where the soul is at that time
        """
        with self.engine.connect() as conn:
            result = conn.execute(
                text("SELECT routines, spawn_location FROM souls WHERE soul_id = :soul_id"),
                {"soul_id": soul_id}
            ).fetchone()
            
            if not result:
                return "soul_plaza"  # Default fallback
            
            routines, spawn_location = result
            
            # If routines exist and have this time slot, use it
            if routines and time_slot.value in routines:
                return routines[time_slot.value]
            
            # Fallback to spawn location
            return spawn_location or "soul_plaza"
    
    def get_world_state(self, user_id: str) -> Dict:
        """
        Get the complete world state for a user's current time slot.
        Returns which souls are where, based on their routines.
        
        Returns:
            {
                "time_slot": "morning",
                "soul_locations": {
                    "aria_01": "echo_archives",
                    "dorian_01": "skylink_tower",
                    ...
                }
            }
        """
        with self.engine.connect() as conn:
            # Get user's current time slot
            user_result = conn.execute(
                text("SELECT current_time_slot FROM users WHERE user_id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            
            if not user_result:
                raise ValueError(f"User {user_id} not found")
            
            current_slot = TimeSlot(user_result[0])
            
            # --- CACHE LOOKUP ---
            with self._cache_lock:
                if current_slot.value in self._world_state_cache:
                    return {
                        "time_slot": current_slot.value,
                        "soul_locations": self._world_state_cache[current_slot.value]
                    }
            
            # Get all souls and their routines/spawn points
            souls_result = conn.execute(
                text("""
                    SELECT s.soul_id, s.routines, s.spawn_location
                    FROM souls s
                """)
            ).fetchall()
            
            # Build soul location map
            soul_locations = {}
            for soul_id, routines, spawn_location in souls_result:
                if routines and current_slot.value in routines:
                    soul_locations[soul_id] = routines[current_slot.value]
                else:
                    soul_locations[soul_id] = spawn_location or "soul_plaza"
            
            # --- UPDATE CACHE ---
            with self._cache_lock:
                self._world_state_cache[current_slot.value] = soul_locations

            return {
                "time_slot": current_slot.value,
                "soul_locations": soul_locations
            }
    
    def get_souls_at_location(self, user_id: str, location_id: str) -> List[str]:
        """
        Get all souls present at a specific location during user's current time slot.
        
        Args:
            user_id: The user's UUID
            location_id: The location to check
        
        Returns:
            List of soul_ids present at that location
        """
        world_state = self.get_world_state(user_id)
        souls_here = [
            soul_id for soul_id, loc in world_state["soul_locations"].items()
            if loc == location_id
        ]
        return souls_here
