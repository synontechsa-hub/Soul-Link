# /backend/app/logic/time_manager.py
# /version.py v1.5.4 Arise
# /_dev/

# "Time is a flat circle."
# - Rust Cohle, True Detective

from sqlalchemy import text, select
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
        
        # 🔑 Invalidate User Profile Cache
        cache_service.delete(f"user:profile:{user_id}")
        
        # 🔑 Invalidate World State Cache for the new time slot
        cache_service.delete(f"world:state:{new_slot.value}")
        
        # 🔑 Invalidate Map Geography Cache (contains soul locations)
        cache_service.delete("map:geography")
        
        # 🚀 REAL-TIME: Send time update to specific user only
        from backend.app.services.websocket_manager import websocket_manager
        from datetime import datetime as dt
        
        await websocket_manager.send_to_user(user_id, {
            "type": "time_advance",
            "data": {
                "previous_slot": current_slot.value,
                "new_time_slot": new_slot.value,
                "timestamp": dt.utcnow().isoformat()
            }
        })
        
        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            from backend.app.core.logging_config import get_logger
            logger = get_logger("TimeManager")
            logger.error(f"Failed to commit time slot change: {e}", exc_info=True)
            raise
        
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
    
    async def get_world_state(self, user_id: str, current_slot: Optional[TimeSlot] = None) -> Dict:
        """
        Get the complete world state for a user at their current time slot.
        """
        if not current_slot:
            user_result = await self.session.execute(
                text("SELECT current_time_slot FROM users WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            user_row = user_result.fetchone()
            
            if not user_row:
                raise ValueError(f"User {user_id} not found")
            
            current_slot = TimeSlot(user_row[0])
        
        cache_key = f"world:state:{current_slot.value}"
        
        # 1. Check Global Cache (Routines + Global Fallbacks)
        cached_data = cache_service.get(cache_key)
        
        if cached_data:
            soul_locations = cached_data.copy()
        else:
            # Fetch all soul IDs
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
            
            # Update cache (1 hour TTL)
            cache_service.set(cache_key, soul_locations, ttl=3600)

        # 2. Layer User-Specific Overrides (Priority 1)
        # These are NEVER cached as they are private to the user
        from backend.app.models.relationship import SoulRelationship
        rel_result = await self.session.execute(
            select(SoulRelationship).where(
                SoulRelationship.user_id == user_id,
                SoulRelationship.current_location.is_not(None)
            )
        )
        overrides = rel_result.scalars().all()
        for rel in overrides:
            soul_locations[rel.soul_id] = rel.current_location

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

    async def warm_world_state_cache(self):
        """
        Pre-calculates and caches the world state for all time slots.
        Run this on startup/background to ensure instant map loads.
        """
        from backend.app.services.location_resolver import LocationResolver
        
        # 1. Fetch all soul IDs once
        souls_result = await self.session.execute(text("SELECT soul_id FROM souls"))
        soul_ids = [row[0] for row in souls_result.fetchall()]
        
        if not soul_ids:
            return

        print(f"🔥 Warming World State Cache for {len(soul_ids)} souls...")

        # 2. OPTIMIZATION: Fetch lightweight Pillar/State data ONCE
        from backend.app.models.soul import SoulPillar, SoulState
        from sqlalchemy.orm import load_only
        
        # Fetch Routines (Lightweight)
        pillar_result = await self.session.execute(
            select(SoulPillar).options(load_only(SoulPillar.soul_id, SoulPillar.routines))
        )
        pillar_map = {p.soul_id: p for p in pillar_result.scalars().all()}
        
        # Fetch Live States (Lightweight)
        state_result = await self.session.execute(select(SoulState))
        state_map = {s.soul_id: s for s in state_result.scalars().all()}

        # 3. Iterate all TimeSlots entirely in memory
        for slot in TimeSlot:
            cache_key = f"world:state:{slot.value}"
            locations = {}
            
            for soul_id in soul_ids:
                # Priority 2: Routine
                pillar = pillar_map.get(soul_id)
                if pillar and pillar.routines:
                    routine_loc = pillar.routines.get(slot.value)
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
            
            # Cache it
            cache_service.set(cache_key, locations, ttl=3600)
            print(f"   ✅ Cached {slot.value}: {len(locations)} locations (In-Memory Fast Path)")
