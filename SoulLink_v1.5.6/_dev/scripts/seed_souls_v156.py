"""
seed_souls_v156.py
Reads all soul JSONs from _dev/data/souls/ and upserts into Supabase.
Architect account is restored automatically via meta_data.dev_config.

Usage:
    python seed_souls_v156.py           # Live run
    python seed_souls_v156.py --dry-run # Preview only, no DB writes
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# ── Path Setup ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import settings
from backend.app.database.session import engine
from backend.app.models.soul import Soul, SoulPillar, SoulState
from sqlmodel import Session, select

# ── Config ───────────────────────────────────────────────────────────────────
SOULS_DIR = PROJECT_ROOT / "_dev" / "data" / "souls"
DRY_RUN = "--dry-run" in sys.argv

SOUL_SUBDIRS = [
    SOULS_DIR,
    SOULS_DIR / "premium_souls",
    SOULS_DIR / "flagship_souls",
]

def load_soul_files():
    files = []
    for d in SOUL_SUBDIRS:
        if d.exists():
            files += [f for f in d.glob("*.json") if not f.name.startswith("_")]
    return files

def seed():
    files = load_soul_files()
    print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}Soul Seeder v1.5.6")
    print(f"Found {len(files)} soul files\n")

    success, failed = 0, 0
    architect_uuid = settings.architect_uuid

    with Session(engine) as session:
        for fpath in sorted(files):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                soul_id = data.get("soul_id")
                if not soul_id:
                    raise ValueError("Missing soul_id")

                pillars = data.get("soul_pillars", {})
                meta = data.get("meta_data", {})

                # Inject architect UUID into dev_config
                dev_config = meta.get("dev_config", {})
                if architect_uuid and architect_uuid not in dev_config.get("architect_ids", []):
                    dev_config.setdefault("architect_ids", []).append(architect_uuid)
                meta["dev_config"] = dev_config

                # Derive routines from interaction_engine schedule if present
                routines = pillars.get("interaction_engine", {}).get("schedule", {})

                if DRY_RUN:
                    print(f"  [PREVIEW] {soul_id} -> name={data.get('name')}, archetype={data.get('archetype')}")
                    success += 1
                    continue

                # ── Upsert Soul ──────────────────────────────────────────────
                existing_soul = session.get(Soul, soul_id)
                if existing_soul:
                    existing_soul.name = data.get("name", soul_id)
                    existing_soul.summary = data.get("short_description", data.get("long_description", "A mysterious soul..."))[:500]
                    existing_soul.portrait_url = f"/assets/images/souls/{soul_id}_01.jpeg"
                    existing_soul.archetype = data.get("archetype")
                    existing_soul.version = data.get("version", "1.5.6")
                    session.add(existing_soul)
                else:
                    soul = Soul(
                        soul_id=soul_id,
                        name=data.get("name", soul_id),
                        summary=data.get("short_description", data.get("long_description", "A mysterious soul..."))[:500],
                        portrait_url=f"/assets/images/souls/{soul_id}_01.jpeg",
                        archetype=data.get("archetype"),
                        version=data.get("version", "1.5.6"),
                        created_at=datetime.utcnow()
                    )
                    session.add(soul)

                session.flush()  # Ensure soul exists before FK references

                # ── Upsert SoulPillar ────────────────────────────────────────
                existing_pillar = session.get(SoulPillar, soul_id)
                pillar_data = dict(
                    soul_id=soul_id,
                    routines=routines,
                    personality=data.get("system_prompt_DNA", {}).get("personality", ""),
                    background=data.get("system_prompt_DNA", {}).get("scenario_drive", ""),
                    identity_pillar=pillars.get("identity_pillar", {}),
                    aesthetic_pillar=pillars.get("aesthetic_pillar", {}),
                    interaction_engine=pillars.get("interaction_engine", {}),
                    llm_instruction_override=data.get("llm_instruction_override", {}),
                    meta_data=meta,
                )
                if existing_pillar:
                    for k, v in pillar_data.items():
                        setattr(existing_pillar, k, v)
                    session.add(existing_pillar)
                else:
                    session.add(SoulPillar(**pillar_data))

                # ── Upsert SoulState ─────────────────────────────────────────
                existing_state = session.get(SoulState, soul_id)
                if not existing_state:
                    session.add(SoulState(
                        soul_id=soul_id,
                        current_location_id="soul_plaza",
                        energy=100,
                        mood="neutral",
                        anxiety_level=0,
                        performance_mode=100,
                        last_updated=datetime.utcnow()
                    ))

                session.commit()
                print(f"  OK {soul_id}")
                success += 1

            except Exception as e:
                session.rollback()
                print(f"  FAIL {fpath.name} -> {e}")
                failed += 1

    print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}Done -> {success} seeded, {failed} failed")

if __name__ == "__main__":
    seed()
