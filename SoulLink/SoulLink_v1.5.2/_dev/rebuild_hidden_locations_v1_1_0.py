# /rebuild_hidden_locations_v1_1_0.py
# /_dev/

# ⚠️ DO NOT RUN BEFORE v1.1.0
# This script introduces non-map, conditionally discoverable locations.
# These locations are NOT visible in the UI and do NOT appear in WORLD_MAP.
# They are triggered implicitly via emotional + narrative state alignment.

import os
from sqlmodel import Session, create_engine, select
from backend.app.models.location import Location

# 🛡️ Secure Credential Fetch
db_password = os.environ.get("SOULLINK_DB_PASS")
if not db_password:
    print("❌ ERROR: SOULLINK_DB_PASS not set.")
    exit(1)

DATABASE_URL = f"postgresql://postgres:{db_password}@localhost:5432/soullink"
engine = create_engine(DATABASE_URL)

# ────────────────────────────────────────────────────────────────
#                   HIDDEN / FRACTURE LOCATIONS
# ────────────────────────────────────────────────────────────────
# These locations exist outside normal traversal logic.
# They should only be referenced by internal state resolvers.

HIDDEN_LOCATIONS = [
    {
        "id": "quiet_interval",
        "name": "The Quiet Interval",
        "desc": (
            "A place that does not exist on any official map. "
            "The air feels thinner here, as if the city briefly forgot to breathe. "
            "Time does not stop — it simply loosens its grip."
        ),
        "mods": {
            "judge": {
                "vulnerability": 1.6,        # exceeds normal soft cap
                "existentialism": 1.4,
                "guard_drop_rate": 0.9       # hard cap edge
            },
            "narrator": {
                "pacing": "suspended",
                "style": "introspective",
                "focus": "inner_world"
            }
        },
        # Stored for later logic resolvers — NOT enforced here
        "unlock_conditions": {
            "requires_flagship_soul": "alyssa",
            "location_chain": ["city_planetarium", "the_garden"],
            "time_window": "late_night",
            "emotional_state": {
                "calm": "high",
                "loneliness": "present"
            }
        }
    }
]

def rebuild_hidden_locations():
    print("🕳️  INITIALIZING HIDDEN LOCATION ARCHIVE (v1.1.0)...")

    with Session(engine) as session:
        for loc_data in HIDDEN_LOCATIONS:
            statement = select(Location).where(Location.location_id == loc_data["id"])
            existing = session.exec(statement).first()

            if existing:
                print(f"🔄 Updating hidden node: {loc_data['name']}")
                existing.display_name = loc_data["name"]
                existing.description = loc_data["desc"]
                existing.system_modifiers = loc_data["mods"]
                existing.hidden = True  # IMPORTANT: UI & map exclusion
                existing.unlock_conditions = loc_data["unlock_conditions"]
                session.add(existing)
            else:
                print(f"✨ Seeding hidden node: {loc_data['name']}")
                new_loc = Location(
                    location_id=loc_data["id"],
                    display_name=loc_data["name"],
                    description=loc_data["desc"],
                    system_modifiers=loc_data["mods"],
                    hidden=True,
                    unlock_conditions=loc_data["unlock_conditions"]
                )
                session.add(new_loc)

        session.commit()
        print("✅ HIDDEN LOCATIONS SEEDED. They will remain dormant.")

if __name__ == "__main__":
    rebuild_hidden_locations()
