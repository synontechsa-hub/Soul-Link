# /scripts/migrate_to_linkstate.py
# v1.5.6 Data Porting Script
# MERGES: UserSoulRelationship + UserSoulState -> LinkState
# NOTE: This script is set to DRY_RUN mode by default.

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlmodel import Session, select, create_engine
from app.models import LinkState, SoulRelationship, UserSoulState
from app.core.config import settings

# --- CONFIG ---
DRY_RUN = True  # Set to False to actually write changes

def migrate_data():
    print("🚀 Starting Mirror System Migration...")
    if DRY_RUN:
        print("⚠️  DRY RUN MODE: No changes will be committed.")
    
    # 1. Connect to DB
    # Ensure DATABASE_URL is set in your env
    db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/soullink") 
    engine = create_engine(db_url)

    with Session(engine) as session:
        # 2. Fetch Sources
        relationships = session.exec(select(SoulRelationship)).all()
        user_states = session.exec(select(UserSoulState)).all()
        
        print(f"Found {len(relationships)} Relationships")
        print(f"Found {len(user_states)} UserSoulStates")
        
        # 3. Create Map for UserStates
        # key: (user_id, soul_id) -> state object
        state_map = {(s.user_id, s.soul_id): s for s in user_states}
        
        new_links = []
        
        # 4. Merge Logic
        for rel in relationships:
            key = (rel.user_id, rel.soul_id)
            state = state_map.get(key)
            
            # Default values if no state record exists
            stability = 100.0
            unlocked_nsfw = rel.nsfw_unlocked # Relationship had this flag too
            
            if state:
                stability = state.signal_stability
                # Prefer strict true if either has it
                unlocked_nsfw = rel.nsfw_unlocked or state.nsfw_enabled
            
            # Create LinkState
            link = LinkState(
                user_id=rel.user_id,
                soul_id=rel.soul_id,
                intimacy_score=rel.intimacy_score,
                intimacy_tier=rel.intimacy_tier,
                current_location=rel.current_location,
                is_architect=rel.is_architect,
                unlocked_nsfw=unlocked_nsfw,
                signal_stability=stability,
                # New fields defaults
                current_mood="neutral",
                mask_integrity=1.0
            )
            new_links.append(link)
        
        print(f"✅ Prepared {len(new_links)} LinkState records.")
        
        # 5. Commit (if not dry run)
        if not DRY_RUN:
            for link in new_links:
                session.add(link)
            session.commit()
            print("💾 COMMITTED to Database.")
        else:
            print("🚫 SKIPPED Commit (Dry Run).")

if __name__ == "__main__":
    migrate_data()
