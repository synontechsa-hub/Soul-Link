# /_dev/scripts/rebirth_v157.py
"""
v1.5.7 Database Rebirth
1. Drops all tables (NUKE).
2. Creates all tables with current SQLModel definitions.
3. Seeds souls (Excluding Architect lore-soul).
4. Seeds locations (Excluding redundant linkside_estate).
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy import text
from sqlmodel import SQLModel, Session, create_engine

# ── Path Setup ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import settings
from backend.app.database.session import engine
from backend.app.models import * # Import all models for metadata

def nuke():
    print("🧨 NUKING DATABASE...")
    with engine.connect() as conn:
        with conn.begin():
            # Standard drop for common tables
            tables = [
                "conversations", "link_states", "soul_memories", 
                "soul_pillars", "soul_states", "souls", "locations", 
                "users", "user_personas", "user_progress", "lore_items",
                "ad_impressions", "soul_relationships", "user_soul_states"
            ]
            for t in tables:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {t} CASCADE"))
                    print(f"  Dropped {t}")
                except Exception as e:
                    print(f"  Error dropping {t}: {e}")

def create_schema():
    print("🏗️ CREATING SCHEMA...")
    SQLModel.metadata.create_all(engine)
    print("  Schema created successfully.")

def seed_souls():
    print("🧬 SEEDING SOULS (Lore Purged)...")
    from _dev.scripts.seed_souls_v156 import load_soul_files, SOULS_DIR
    
    files = load_soul_files()
    success = 0
    
    with Session(engine) as session:
        for fpath in sorted(files):
            if fpath.name == "the_architect_01.json":
                print(f"  [SKIP] {fpath.name} (Lore Entity Identified)")
                continue

            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            soul_id = data.get("soul_id")
            identity = data.get("identity", {})
            
            # --- Upsert Soul ---
            soul = Soul(
                soul_id=soul_id,
                name=identity.get("name", data.get("name", soul_id)),
                summary=identity.get("summary", data.get("short_description", ""))[:500],
                portrait_url=data.get("aesthetic", {}).get("portrait_path", f"/assets/images/souls/{soul_id}_01.jpeg"),
                archetype=identity.get("archetype_id", data.get("archetype")),
                version="1.5.7",
                created_at=datetime.utcnow()
            )
            session.add(soul)

            # --- Upsert Pillar ---
            pillar = SoulPillar(
                soul_id=soul_id,
                identity=data.get("identity", {}),
                aesthetic=data.get("aesthetic", {}),
                systems_config=data.get("systems_config", {}),
                routine=data.get("routine", {}),
                inventory=data.get("inventory", {}),
                relationships=data.get("relationships", {}),
                lore_associations=data.get("lore_associations", {}),
                interaction_system=data.get("interaction_system", {}),
                prompts=data.get("prompts", {}),
                meta_data=data.get("meta_data", {}),
                routines={} # Minimal seed, runtime will resolve
            )
            session.add(pillar)

            # --- Upsert State ---
            state = SoulState(
                soul_id=soul_id,
                current_location_id="soul_plaza",
                energy=100,
                mood="neutral",
                anxiety_level=0,
                performance_mode=100,
                last_updated=datetime.utcnow()
            )
            session.add(state)
            
            success += 1

        session.commit()
    print(f"  Seeded {success} souls.")

def seed_locations():
    print("🗺️ SEEDING LOCATIONS (Optimized)...")
    loc_dir = PROJECT_ROOT / "_dev" / "data" / "locations"
    files = [f for f in loc_dir.glob("*.json") if not f.name.startswith("_")]
    
    success = 0
    with Session(engine) as session:
        for fpath in sorted(files):
            if fpath.name == "linkside_estate.json":
                print(f"  [SKIP] {fpath.name} (Redundant Map Entry)")
                continue
                
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            loc_id = data.get("location_id")
            meta = data.get("meta", {})
            game_logic = data.get("game_logic", {})
            entry_rules = game_logic.get("entry_rules", {})

            loc = Location(
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
            session.add(loc)
            success += 1
            
        session.commit()
    print(f"  Seeded {success} locations.")

if __name__ == "__main__":
    nuke()
    create_schema()
    seed_souls()
    seed_locations()
    print("\n✅ v1.5.7 REBIRTH COMPLETE.")
