"""
seed_locations_v156.py
Reads all location JSONs from _dev/data/locations/ and upserts into Supabase.

Usage:
    python seed_locations_v156.py           # Live run
    python seed_locations_v156.py --dry-run # Preview only, no DB writes
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# ── Path Setup ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.session import engine
from backend.app.models.location import Location
from sqlmodel import Session

# ── Config ───────────────────────────────────────────────────────────────────
LOCATIONS_DIR = PROJECT_ROOT / "_dev" / "data" / "locations"
DRY_RUN = "--dry-run" in sys.argv

def seed():
    files = [f for f in LOCATIONS_DIR.glob("*.json") if not f.name.startswith("_")]
    print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}Location Seeder v1.5.6")
    print(f"Found {len(files)} location files\n")

    success, failed = 0, 0

    with Session(engine) as session:
        for fpath in sorted(files):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                loc_id = data.get("location_id")
                if not loc_id:
                    raise ValueError("Missing location_id")

                meta = data.get("meta", {})
                game_logic = data.get("game_logic", {})
                entry_rules = game_logic.get("entry_rules", {})
                privacy = data.get("system_modifiers", {}).get("privacy_gate", "Public")

                if DRY_RUN:
                    print(f"  [PREVIEW] {loc_id} -> {meta.get('display_name')} [{privacy}]")
                    success += 1
                    continue

                existing = session.get(Location, loc_id)
                loc_data = dict(
                    location_id=loc_id,
                    display_name=meta.get("display_name", loc_id),
                    category=meta.get("category"),
                    description=meta.get("description", ""),
                    image_url=meta.get("image_url", f"/assets/images/locations/{loc_id}_01.jpg"),
                    music_track="ambient_city_loop.mp3",
                    system_modifiers=data.get("system_modifiers", {"privacy_gate": "Public"}),
                    system_prompt_anchors=data.get("system_prompt_anchors", {}),
                    game_logic=game_logic,
                    lore=data.get("lore", {}),
                    source_metadata=data.get("metadata", {}),
                    min_intimacy=entry_rules.get("min_intimacy", 0),
                )

                if existing:
                    for k, v in loc_data.items():
                        setattr(existing, k, v)
                    session.add(existing)
                else:
                    session.add(Location(**loc_data))

                session.commit()
                print(f"  OK {loc_id}")
                success += 1

            except Exception as e:
                session.rollback()
                print(f"  FAIL {fpath.name} -> {e}")
                failed += 1

    print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}Done -> {success} seeded, {failed} failed")

if __name__ == "__main__":
    seed()
