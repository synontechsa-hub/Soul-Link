# /backend/app/logic/location_manager.py
# /version.py
# /_dev/

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from backend.app.models.relationship import SoulRelationship
from backend.app.models.location import Location

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
        Handles the movement logic asynchronously.
        
        Args:
            user_id: The UUID of the user requesting the move.
            soul_id: The ID of the soul being moved.
            location_id: The target destination.
        
        Returns:
            (bool, str): Success status and descriptive message.
        """
        # (Rest of the move_to logic remains same but can now use check_eligibility internally)
        can_move, msg = await self.check_eligibility(user_id, soul_id, location_id)
        if not can_move:
            return False, msg

        # 1. Verify location exists in the geography (already done by check_eligibility, but need loc for message)
        loc = await self.session.get(Location, location_id)
        # 2. Fetch the current Relationship state (already done by check_eligibility, but need rel for update)
        rel_result = await self.session.execute(
            select(SoulRelationship).where(
                SoulRelationship.user_id == user_id,
                SoulRelationship.soul_id == soul_id
            )
        )
        rel = rel_result.scalars().first()

        # 🛡️ THE GATEKEEPER CHECK (now handled by check_eligibility)

        # 3. Execute the move
        try:
            rel.current_location = location_id
            self.session.add(rel)
            await self.session.commit()
            
            return True, f"Synchronized. Welcome to {loc.display_name}."
        except Exception as e:
            return False, f"Teleportation Error: {str(e)}"