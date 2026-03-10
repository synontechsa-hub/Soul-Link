"""
seed_lore_v156.py
Seeds lore knowledge items from lore.json into the lore_items DB table.

Usage:
    python seed_lore_v156.py           # Live run
    python seed_lore_v156.py --dry-run # Preview only
"""
from sqlmodel import Session
from backend.app.models.lore_item import LoreItem
from backend.app.database.session import engine
import sys
import json
import os
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, r"d:\Coding\SynonTech\SoulLink\SoulLink_v1.5.6")
DATA_DIR = Path(r"d:\Coding\SynonTech\SoulLink\SoulLink_v1.5.6\_dev\data")


LORE_FILE = DATA_DIR / "system" / "lore.json"
DRY_RUN = "--dry-run" in sys.argv


def seed():
    print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}Lore Seeder v1.5.6")

    if not LORE_FILE.exists():
        print(f"  ERROR: {LORE_FILE} not found")
        return

    with open(LORE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("knowledge_items", [])
    print(f"Found {len(items)} lore items\n")
    success, failed = 0, 0

    with Session(engine) as session:
        for item in items:
            item_id = item.get("id")
            if not item_id:
                continue
            try:
                if DRY_RUN:
                    print(f"  [PREVIEW] {item_id} [{item.get('category')}]")
                    success += 1
                    continue

                existing = session.get(LoreItem, item_id)
                lore_data = dict(
                    id=item_id,
                    category=item.get("category", "general"),
                    topics=item.get("topics", []),
                    content=item.get("content", {}),
                    associations=item.get("associations", {}),
                    source_metadata={
                        "source": "lore.json", "version": "1.5.6"},
                    version="1.5.6",
                    updated_at=datetime.now(timezone.utc)
                )

                if existing:
                    for k, v in lore_data.items():
                        setattr(existing, k, v)
                    session.add(existing)
                else:
                    session.add(LoreItem(**lore_data))

                session.commit()
                print(f"  OK {item_id}")
                success += 1
            except Exception as e:
                session.rollback()
                print(f"  FAIL {item_id} → {e}")
                failed += 1

    print(
        f"\n{'[DRY RUN] ' if DRY_RUN else ''}Done → {success} seeded, {failed} failed")


if __name__ == "__main__":
    seed()
