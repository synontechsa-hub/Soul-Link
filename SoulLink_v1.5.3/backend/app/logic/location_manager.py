# /backend/app/logic/location_manager.py
# /version.py
# /_dev/

from sqlmodel import Session, select
from backend.app.models.relationship import SoulRelationship
from backend.app.models.location import Location

class LocationManager:
    def __init__(self, engine):
        self.engine = engine

    def move_to(self, user_id: str, soul_id: str, location_id: str):
        """
        Handles the movement logic within Link City.
        Includes Gatekeeper checks for intimacy-locked districts.
        """
        with Session(self.engine) as session:
            
            # 1. Verify location exists in the geography
            loc = session.get(Location, location_id)
            if not loc:
                return False, f"Location {location_id} doesn't exist."

            # 2. Fetch the current Relationship state
            rel = session.exec(
                select(SoulRelationship).where(
                    SoulRelationship.user_id == user_id,
                    SoulRelationship.soul_id == soul_id
                )
            ).first()

            if not rel:
                return False, "Link not found. You must establish a link with this Soul first."

            # 🛡️ THE GATEKEEPER CHECK
            # We check if the user has enough intimacy for this location.
            # USR-001 (The Architect) ignores these laws.
            if user_id != "USR-001":
                if rel.intimacy_score < loc.min_intimacy:
                    return False, f"Access Denied: You need more intimacy to enter {loc.display_name}."

            # 3. Execute the move
            try:
                rel.current_location = location_id
                session.add(rel)
                session.commit()
                
                # We return a success message that the frontend can display
                return True, f"Synchronized. Welcome to {loc.display_name}."
            except Exception as e:
                return False, f"Teleportation Error: {str(e)}"