import json
import os
import sys
from pathlib import Path

# Setup Environment
SCRIPT_DIR = Path(__file__).resolve().parent
DEV_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = DEV_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.models.location import Location
from backend.app.models.lore_item import LoreItem
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlmodel import select

# Database Connection (Adjust if needed for production)

# Database Connection (Adjust if needed for production)
DB_PATH = PROJECT_ROOT / "backend/soul_link.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL)

BLUEPRINTS_DIR = DEV_DIR / "blueprints"

def init_db():
    from sqlmodel import SQLModel
    print("🛠️ Initializing Database Schema...")
    SQLModel.metadata.create_all(engine)
    print("✅ Database Schema Ready.")

def load_locations(session: Session):
    """Load all Location JSONs into the database."""
    loc_dir = BLUEPRINTS_DIR / "locations"
    print(f"🌍 Loading Locations from {loc_dir}...")
    
    files = list(loc_dir.glob("*.json"))
    count = 0
    
    for file_path in files:
        if file_path.name in ["template.json", "known_locations.json"]:
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Extract fields based on new schema
        loc_id = data.get("location_id")
        meta = data.get("meta", {})
        
        # Construct Location object
        location = Location(
            location_id=loc_id,
            display_name=meta.get("display_name"),
            category=meta.get("category"),
            description=meta.get("description"),
            image_url=meta.get("image_url"),
            min_intimacy=data.get("game_logic", {}).get("entry_rules", {}).get("min_intimacy", 0),
            
            # JSON Columns
            system_prompt_anchors=data.get("system_prompt_anchors", {}),
            game_logic=data.get("game_logic", {}),
            lore=data.get("lore", {}),
            source_metadata=data.get("metadata", {})
        )
        
        # Upsert (Merge)
        session.merge(location)
        count += 1
        
    session.commit()
    print(f"✅ Loaded {count} Locations.")

def load_lore(session: Session):
    """Load Lore Items from the template/aggregated file."""
    lore_file = BLUEPRINTS_DIR / "lore/template.json"
    if not lore_file.exists():
        print("⚠️ No lore template found, skipping.")
        return

    print(f"📜 Loading Lore from {lore_file}...")
    
    with open(lore_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    items = data.get("knowledge_items", [])
    count = 0
    
    for item in items:
        lore_item = LoreItem(
            id=item["id"],
            category=item["category"],
            topics=item["topics"],
            content=item["content"],
            associations=item["associations"],
            source_metadata=data.get("metadata", {})
        )
        session.merge(lore_item)
        count += 1
        
    session.commit()
    print(f"✅ Loaded {count} Lore Items.")

def main():
    print("🚀 Starting World Seed (v1.5.5)...")
    init_db()
    with Session(engine) as session:
        load_locations(session)
        load_lore(session)
    print("✨ World Seed Complete!")

if __name__ == "__main__":
    main()
