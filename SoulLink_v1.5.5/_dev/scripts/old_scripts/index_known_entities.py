import json
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
LOC_DIR = BASE_DIR / "blueprints/locations"
SOUL_DIR = BASE_DIR / "character_sheets"
KNOWN_LOCS_FILE = LOC_DIR / "known_locations.json"
KNOWN_SOULS_FILE = BASE_DIR / "blueprints/souls/known_souls.json"

def index_locations():
    print("🌍 Indexing Locations...")
    locs = []
    for file_path in sorted(LOC_DIR.glob("*.json")):
        if file_path.name in ["known_locations.json", "template.json"]:
            continue
        
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # handle either v1.5.5 schema or simple meta
                loc_id = data.get("location_id") or data.get("id")
                meta = data.get("meta", {})
                name = meta.get("display_name") or data.get("name") or file_path.stem.replace("_", " ").title()
                desc = meta.get("description") or data.get("description") or "Auto-indexed location"
                
                if loc_id:
                    locs.append({"id": loc_id, "name": name, "description": desc})
            except Exception as e:
                print(f"  ⚠️ Error reading {file_path.name}: {e}")
    
    with open(KNOWN_LOCS_FILE, "w", encoding="utf-8") as f:
        json.dump(locs, f, indent=4)
    print(f"✅ Indexed {len(locs)} locations.")

def index_souls():
    print("👤 Indexing Souls...")
    souls = []
    for file_path in sorted(SOUL_DIR.glob("*.txt")):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            id_match = re.search(r'Soul ID:\s*(\w+)', content)
            if id_match:
                souls.append(id_match.group(1))
            else:
                # fall back to lowercase filename if no ID found
                souls.append(file_path.stem.lower())
    
    with open(KNOWN_SOULS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(set(souls))), f, indent=2)
    print(f"✅ Indexed {len(souls)} souls.")

if __name__ == "__main__":
    index_locations()
    index_souls()
