from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from backend.app.models.link_state import LinkState
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

        link_result = await self.session.execute(
            select(LinkState).where(
                LinkState.user_id == user_id,
                LinkState.soul_id == soul_id
            )
        )
        link = link_result.scalars().first()
        if not link:
            return False, "No link established."

        # Rules
        if not link.is_architect:
            if link.intimacy_score < loc.min_intimacy:
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
        
        # Fetch LinkState
        link_result = await self.session.execute(
            select(LinkState).where(
                LinkState.user_id == user_id,
                LinkState.soul_id == soul_id
            )
        )
        link = link_result.scalars().first()

        try:
            # 1. Update User Context (manual override - Priority 1)
            link.current_location = location_id
            self.session.add(link)
            
            # 2. COMMIT the change
            await self.session.commit()
            
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
            await self.session.rollback()
            return False, f"Teleportation Error: {str(e)}"
