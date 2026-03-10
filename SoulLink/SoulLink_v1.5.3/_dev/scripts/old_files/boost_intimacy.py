# /_dev/scripts/boost_intimacy.py
# /version.py

import sys
from pathlib import Path
from sqlmodel import Session, create_engine, select

# Pathing
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.models.relationship import SoulRelationship
from backend.app.core.config import settings

# Vroom!
engine = create_engine(settings.database_url)

# Tier thresholds (matching your actual system)
TIER_THRESHOLDS = {
    "STRANGER": 0,
    "ACQUAINTANCE": 21,
    "TRUSTED": 41,
    "FRIENDSHIP": 71,
    "SOUL_LINKED": 86
}

def get_tier_for_score(score: int) -> str:
    """Calculate tier based on intimacy score"""
    if score >= 86:
        return "SOUL_LINKED"
    elif score >= 71:
        return "FRIENDSHIP"
    elif score >= 41:
        return "TRUSTED"
    elif score >= 21:
        return "ACQUAINTANCE"
    else:
        return "STRANGER"

def boost(user_id: str, soul_id: str, points: int):
    """Boost intimacy for any user, not just USR-001"""
    with Session(engine) as session:
        rel = session.exec(
            select(SoulRelationship).where(
                SoulRelationship.user_id == user_id,
                SoulRelationship.soul_id == soul_id
            )
        ).first()

        if not rel:
            print(f"❌ No relationship found between {user_id} and {soul_id}")
            print(f"💡 Tip: Use /souls/{soul_id}/link endpoint to create relationship first")
            return

        old_tier = rel.intimacy_tier
        old_score = rel.intimacy_score
        
        rel.intimacy_score += points
        new_tier = get_tier_for_score(rel.intimacy_score)
        rel.intimacy_tier = new_tier
        
        session.add(rel)
        session.commit()
        
        # Display results
        if new_tier != old_tier:
            print(f"✨ TIER UP! {soul_id}: {old_tier} → {new_tier}")
        
        print(f"📈 Intimacy: {old_score} → {rel.intimacy_score} (Tier: {rel.intimacy_tier})")

if __name__ == "__main__":
    # Parse command line args
    if len(sys.argv) < 3:
        print("Usage: python boost_intimacy.py <user_id> <soul_id> [points]")
        print("\nExamples:")
        print("  python boost_intimacy.py USR-001 evangeline_01 20")
        print("  python boost_intimacy.py USR-A3F2B8C1 adrian_01 50")
        print("\n💡 Default points: 20")
        sys.exit(1)
    
    user_id = sys.argv[1]
    soul_id = sys.argv[2]
    points = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    
    # "Quad Damage!"
    # - Quake
    boost(user_id, soul_id, points)

# Heyy.... speaking of quake. That was an epic game. The first 1... 2 and 3 were meh...
# THE NAILGUN!
