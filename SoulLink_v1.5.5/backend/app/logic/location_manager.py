from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from backend.app.models.relationship import SoulRelationship
from backend.app.models.location import Location
from backend.app.models.soul import SoulState
from backend.app.core.cache import cache_service
from datetime import datetime

class LocationManager:
    """
    Handles movement of souls between locations in Link City.
    Ensures Gatekeeper rules (Privacy/Intimacy/Architect) are enforced.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_eligibility(self, user_id: str, soul_id: str, location_id: str):
        """Checks if a user can bring a soul to a location."""
        loc = await self.session.get(Location, location_id)
        if not loc:
            return False, "Unknown location."

        rel_result = await self.session.execute(
            select(SoulRelationship).where(
                SoulRelationship.user_id == user_id,
                SoulRelationship.soul_id == soul_id
            )
        )
        rel = rel_result.scalars().first()
        if not rel:
            return False, "No link established."

        # Rules
        if not rel.is_architect:
            if rel.intimacy_score < loc.min_intimacy:
                return False, f"Requires {loc.min_intimacy} intimacy."

        return True, "Eligible."

    async def move_to(self, user_id: str, soul_id: str, location_id: str):
        """
        Handles the movement logic asynchronously, updating global SoulState.
        """
        can_move, msg = await self.check_eligibility(user_id, soul_id, location_id)
        if not can_move:
            return False, msg

        loc = await self.session.get(Location, location_id)
        
        # Fetch Relationship
        rel_result = await self.session.execute(
            select(SoulRelationship).where(
                SoulRelationship.user_id == user_id,
                SoulRelationship.soul_id == soul_id
            )
        )
        rel = rel_result.scalars().first()

        # Fetch Global State
        state = await self.session.get(SoulState, soul_id)

        try:
            # 1. Update User Context (manual override - Priority 1)
            # This ensures the move is private and won't affect other users.
            rel.current_location = location_id
            self.session.add(rel)
            
            # 2. DO NOT update Global State (Priority 3) for player-led moves.
            # Global state updates are reserved for world-level events or Architect edits.
            # (Deleted: LocationResolver.update_global_location call)
            
            # 3. Cache Invalidation: Global world state is now stale
            cache_service.delete_pattern("world:state:*")
            
            # 4. 🚀 REAL-TIME: Broadcast location update via WebSocket
            from backend.app.services.websocket_manager import websocket_manager
            from datetime import datetime as dt
            
            await websocket_manager.broadcast_to_all({
                "type": "location_update",
                "data": {
                    "soul_id": soul_id,
                    "location_id": location_id,
                    "location_name": loc.display_name
                },
                "timestamp": dt.utcnow().isoformat()
            })
            
            return True, f"Synchronized. Welcome to {loc.display_name}."
        except Exception as e:
            return False, f"Teleportation Error: {str(e)}"
