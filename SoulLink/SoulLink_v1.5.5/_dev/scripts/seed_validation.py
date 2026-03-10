import asyncio
import os
import sys
import json
from pathlib import Path
from sqlalchemy import text, select
from sqlalchemy.orm import load_only

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.app.database.session import async_session_maker
from backend.app.models.soul import Soul, SoulPillar
from backend.app.models.location import Location

BLUEPRINTS_DIR = Path(__file__).resolve().parent.parent / "blueprints"

async def validate_seed_integrity():
    print("🔍 Starting Seed Integrity Validation...")
    
    async with async_session_maker() as session:
        # 1. Load Blueprints
        blueprint_souls = []
        blueprint_routines = {}
        
        if not BLUEPRINTS_DIR.exists():
            print(f"❌ Blueprints directory not found: {BLUEPRINTS_DIR}")
            return

        for fail in BLUEPRINTS_DIR.glob("*.json"):
            try:
                with open(fail, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sid = data.get("soul_id")
                    if sid:
                        blueprint_souls.append(sid)
                        # Extract expected routines from meta if present
                        if "meta" in data and "routines" in data["meta"]:
                            blueprint_routines[sid] = data["meta"]["routines"]
            except Exception as e:
                print(f"⚠️ Failed to read blueprint {fail.name}: {e}")

        print(f"📄 Found {len(blueprint_souls)} souls in blueprints.")

        # 2. Verify Souls in DB
        db_souls_result = await session.execute(select(Soul.soul_id))
        db_souls = set(db_souls_result.scalars().all())
        
        missing_souls = [s for s in blueprint_souls if s not in db_souls]
        
        if missing_souls:
            print(f"❌ CRITICAL: {len(missing_souls)} souls missing from DB!")
            for s in missing_souls:
                print(f"   - {s}")
        else:
            print("✅ All blueprint souls verify present in DB.")

        # 3. Verify Body Pillars & Routines
        print("\n🧠 Verifying Logic Pillars...")
        pillar_result = await session.execute(select(SoulPillar))
        pillars = pillar_result.scalars().all()
        pillar_map = {p.soul_id: p for p in pillars}
        
        missing_pillars = [s for s in blueprint_souls if s not in pillar_map]
        if missing_pillars:
             print(f"❌ CRITICAL: {len(missing_pillars)} souls missing Logic Pillars!")
        
        routine_issues = 0
        for soul_id, routine_data in blueprint_routines.items():
            pillar = pillar_map.get(soul_id)
            if not pillar: 
                continue # Already reported
                
            db_routines = pillar.routines
            if not db_routines:
                print(f"⚠️ Soul {soul_id} has NO routines in DB (Expected from blueprint)!")
                routine_issues += 1
                continue
                
            # Check slot match
            for slot, loc in routine_data.items():
                if slot not in db_routines:
                     print(f"⚠️ Soul {soul_id} missing routine for {slot}!")
                     routine_issues += 1
                elif db_routines[slot] != loc:
                     print(f"⚠️ Routine Mismatch {soul_id} [{slot}]: Expected {loc}, Got {db_routines[slot]}")
                     routine_issues += 1

        if routine_issues == 0:
            print("✅ Routines verified against blueprints.")
        
        # 4. Verify Locations Exist
        print("\nbfs🗺️ Verifying Location Integrity...")
        
        # Collect all referenced locations in routines
        referenced_locs = set()
        for p in pillars:
            if p.routines:
                referenced_locs.update(p.routines.values())
        
        # Fetch real locations
        loc_result = await session.execute(select(Location.location_id))
        real_locs = set(loc_result.scalars().all())
        
        # Add system defaults
        real_locs.add("soul_plaza")
        real_locs.add("limbo")
        
        invalid_locs = [l for l in referenced_locs if l not in real_locs]
        
        if invalid_locs:
            print(f"❌ CRITICAL: Routines reference non-existent locations!")
            for l in invalid_locs:
                print(f"   - {l}")
        else:
            print("✅ All routine locations exist in the world.")

    print("\n🏁 Validation Complete.")

if __name__ == "__main__":
    asyncio.run(validate_seed_integrity())
