# /_dev/scripts/seed_db.py
# /version.py v1.5.4 Arise

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

# Path setup
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

# Load root .env
load_dotenv(project_root / ".env")

from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session, select
from backend.app.models.soul import Soul
from backend.app.models.location import Location
from backend.app.models.relationship import SoulRelationship
from backend.app.models.user import User
from version import VERSION_SHORT, CURRENT_CODENAME

# "War, war never changes." - Fallout
DATABASE_URL = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ ERROR: Neither SUPABASE_DB_URL nor DATABASE_URL found in .env!")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

def init_db():
    print(f"🔥 {CURRENT_CODENAME} Rising: Initializing soul_link_db...")
    SQLModel.metadata.create_all(engine)
    print("✅ Tables verified/created successfully")

def ensure_architect_exists():
    """Checks if the Architect exists based on ARCHITECT_UUID env var.
    If missing, creates a stub. If present, ensures 'architect' tier.
    """
    architect_id = os.getenv("ARCHITECT_UUID")
    if not architect_id or "[YOUR-ID-GOES-HERE]" in architect_id:
        print("⚠️ ARCHITECT_UUID not found or not set in .env. Skipping Architect check.")
        return None

    with Session(engine) as session:
        architect = session.get(User, architect_id)
        if not architect:
            print(f"✨ Creating Architect User Record ({architect_id})...")
            architect = User(
                user_id=architect_id,
                username="TheArchitect",
                display_name="The Architect",
                account_tier="architect"
            )
            session.add(architect)
        else:
            if architect.account_tier != "architect":
                print(f"🔝 Promoting {architect.username} to Architect tier...")
                architect.account_tier = "architect"
                session.add(architect)
            print(f"✅ Architect Profile active: {architect.display_name or architect.username}")
        
        session.commit()
        return architect_id

def seed_souls(architect_id):
    """Syncs Soul Blueprints from _dev/blueprints and links them to the Architect"""
    blueprint_path = project_root / "_dev" / "blueprints"
    
    if not blueprint_path.exists():
        print(f"⚠️  Blueprint folder not found: {blueprint_path}")
        return
    
    # Filter for JSONs and ignore templates
    json_files = [f for f in blueprint_path.glob("*.json") if "_template" not in f.name]
    print(f"🧬 Syncing {len(json_files)} Souls to the Hive...")

    with Session(engine) as session:
        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                
                soul_id = raw_data.get("soul_id")
                meta = raw_data.get("meta", {})
                soul_name = meta.get("name", "Unknown")
                
                if not soul_id:
                    continue

                # Prepare the fields
                updated_fields = {
                    "name": soul_name,
                    "version": meta.get("version", VERSION_SHORT),
                    "archetype": meta.get("archetype", "Unknown"),
                    "summary": meta.get("summary", "A mysterious soul..."),
                    "personality": raw_data.get("identity_pillar", {}).get("bio", ""),
                    "portrait_url": meta.get("portrait_full"), 
                    "spawn_location": meta.get("starting_location", "soul_plaza"),
                    "identity_pillar": raw_data.get("identity_pillar", {}),
                    "aesthetic_pillar": raw_data.get("aesthetic_pillar", {}),
                    "interaction_engine": raw_data.get("interaction_engine", {}),
                    "llm_instruction_override": raw_data.get("llm_instruction_override", {}),
                    "meta_data": meta
                }

                # --- DB SYNC ---
                existing = session.get(Soul, soul_id)
                if existing:
                    print(f"  🔄 Updating: {soul_name}")
                    for key, value in updated_fields.items():
                        setattr(existing, key, value)
                else:
                    print(f"  ✨ Creating: {soul_name}")
                    new_soul = Soul(soul_id=soul_id, **updated_fields)
                    session.add(new_soul)

                session.flush() # Sync so we can link the relationship

                # --- ARCHITECT LINK (Auto-max intimacy for dev) ---
                if architect_id:
                    # Check if default loft exists
                    loc_check = session.exec(select(Location).where(Location.location_id == "linkside_estate")).first()
                    start_loc = "linkside_estate" if loc_check else None

                    existing_rel = session.exec(
                        select(SoulRelationship).where(
                            SoulRelationship.user_id == architect_id,
                            SoulRelationship.soul_id == soul_id
                        )
                    ).first()

                    if not existing_rel:
                        architect_link = SoulRelationship(
                            user_id=architect_id,
                            soul_id=soul_id,
                            intimacy_score=100,
                            intimacy_tier="SOUL_LINKED",
                            is_architect=True,
                            nsfw_unlocked=True,
                            current_location=start_loc
                        )
                        session.add(architect_link)
                        print(f"    🔗 Bound {soul_name} to Architect.")
                
            except Exception as e:
                print(f"❌ Error processing {json_file.name}: {e}")

        session.commit()
        print(f"\n💾 All v{VERSION_SHORT} ({CURRENT_CODENAME}) Souls and Architect links successfully committed.")

if __name__ == "__main__":
    print("--- STARTING SOULLINK SEEDER ---")
    init_db()
    arch_id = ensure_architect_exists()
    seed_souls(arch_id)
    print("--- SEEDING COMPLETE ---")