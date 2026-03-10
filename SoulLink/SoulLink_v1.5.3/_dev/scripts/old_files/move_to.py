# /_dev/scripts/move_to.py
# /version.py

import sys
from pathlib import Path
from sqlmodel import Session, create_engine, select

script_path = Path(__file__).resolve()
project_root = script_path.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.models.relationship import SoulRelationship
from backend.app.models.location import Location
from backend.app.core.config import settings

engine = create_engine(settings.database_url)

def teleport(user_id: str, soul_id: str, loc_id: str):
    """Teleport a soul to a new location for any user"""
    with Session(engine) as session:
        # Check if location exists
        loc = session.get(Location, loc_id)
        if not loc:
            print(f"❌ Error: Location '{loc_id}' not found in DB.")
            print("\n💡 Available locations:")
            all_locs = session.exec(select(Location)).all()
            for l in all_locs:
                print(f"  - {l.location_id}: {l.display_name}")
            return

        # Update relationship
        rel = session.exec(
            select(SoulRelationship).where(
                SoulRelationship.user_id == user_id,
                SoulRelationship.soul_id == soul_id
            )
        ).first()

        if rel:
            rel.current_location = loc_id
            session.add(rel)
            session.commit()
            print(f"🏙️  Teleported {soul_id} to: {loc.display_name}")
            print(f"📝 Description: {loc.description}")
        else:
            print(f"❌ Error: No relationship found between {user_id} and {soul_id}")
            print(f"💡 Tip: Use /souls/{soul_id}/link endpoint to create relationship first")

if __name__ == "__main__":
    # Parse command line args
    if len(sys.argv) < 3:
        print("Usage: python move_to.py <user_id> <soul_id> [location_id]")
        print("\nExamples:")
        print("  python move_to.py USR-001 evangeline_01 linkgate_mall")
        print("  python move_to.py USR-A3F2B8C1 adrian_01 stop_n_go_racetrack")
        print("\n💡 Default location: stop_n_go_racetrack")
        sys.exit(1)
    
    user_id = sys.argv[1]
    soul_id = sys.argv[2]
    loc_id = sys.argv[3] if len(sys.argv) > 3 else "stop_n_go_racetrack"
    
    teleport(user_id, soul_id, loc_id)
