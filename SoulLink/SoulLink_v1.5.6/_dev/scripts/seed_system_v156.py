"""
seed_system_v156.py
Seeds all system JSON configs into the system_config DB table.

Keys seeded: weather, time_and_day, calendar, archetypes, factions,
             routines, intimacy, relationships, monetization, global_config

Usage:
    python seed_system_v156.py           # Live run
    python seed_system_v156.py --dry-run # Preview only
"""
from sqlmodel import Session
from backend.app.models.system_config import SystemConfig
from backend.app.database.session import engine
import sys
import json
import os
from pathlib import Path

sys.path.insert(0, r"d:\Coding\SynonTech\SoulLink\SoulLink_v1.5.6")
DATA_DIR = Path(r"d:\Coding\SynonTech\SoulLink\SoulLink_v1.5.6\_dev\data")


SYSTEM_DIR = DATA_DIR / "system"
DRY_RUN = "--dry-run" in sys.argv

# Map: DB key → filename
SYSTEM_FILES = {
    "weather":       "weather.json",
    "time_and_day":  "time_and_day.json",
    "calendar":      "calendar.json",
    "archetypes":    "archetypes.json",
    "factions":      "factions.json",
    "routines":      "routines.json",
    "intimacy":      "intimacy.json",
    "relationships": "relationships.json",
    "monetization":  "monetization.json",
    "global_config": "global_config.json",
}


def seed():
    print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}System Config Seeder v1.5.6")
    print(f"Reading from: {SYSTEM_DIR}\n")
    success, failed, skipped = 0, 0, 0

    with Session(engine) as session:
        for key, filename in SYSTEM_FILES.items():
            fpath = SYSTEM_DIR / filename
            if not fpath.exists():
                print(f"  SKIP {key} — {filename} not found")
                skipped += 1
                continue
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if DRY_RUN:
                    print(f"  [PREVIEW] {key} ← {filename}")
                    success += 1
                    continue

                existing = session.get(SystemConfig, key)
                if existing:
                    existing.data = data
                    existing.version = data.get("version", "1.5.6")
                    session.add(existing)
                else:
                    session.add(SystemConfig(
                        key=key,
                        data=data,
                        version=data.get("version", "1.5.6")
                    ))

                session.commit()
                print(f"  OK {key}")
                success += 1
            except Exception as e:
                session.rollback()
                print(f"  FAIL {key} → {e}")
                failed += 1

    print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}Done → {success} seeded, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    seed()
