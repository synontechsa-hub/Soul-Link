# /import_standard_soul.py
# /version.py
# /_dev/

import json
import os
import sys
from sqlmodel import Session, select
from backend.app.models.soul import Soul
from backend.app.database.session import engine

# “It's dangerous to go alone! Take this.”
# - The Old Man - The Legend of Zelda

def import_soul_from_folder(soul_folder_name: str):
    """
    Looks into /souls/[soul_folder_name]/
    Stitches core, context, and metadata into the 1.5.2 Architect Schema.
    """
    base_path = f"souls/{soul_folder_name}"
    
    if not os.path.exists(base_path):
        print(f"❌ Error: Folder '{base_path}' not found.")
        return

    # 1. LOAD DATA PIECES (Forcing UTF-8 to kill the UnicodeDecodeError)
    def load_json(filename):
        path = os.path.join(base_path, filename)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Warning: Could not load {filename} in {soul_folder_name}: {e}")
        return {}

    core_data = load_json("core.json")
    context_data = load_json("context.json")
    metadata_data = load_json("metadata.json")

    if not core_data:
        # We'll just skip silently if it's an empty folder or not a soul folder
        return

    # Extract soul_id from the 'meta' block in your core.json
    soul_id = core_data.get("meta", {}).get("id")
    if not soul_id:
        print(f"🛑 Critical: No 'soul_id' found in {soul_folder_name}/core.json")
        return

    with Session(engine) as session:
        statement = select(Soul).where(Soul.soul_id == soul_id)
        soul = session.exec(statement).first()

        if not soul:
            print(f"✨ Creating: {soul_id}")
            soul = Soul(soul_id=soul_id) # type: ignore[call-arg]
        else:
            print(f"🔄 Updating: {soul_id}")

        # Map basic info from the 'identity' and 'meta' blocks
        identity = core_data.get("identity", {})
        soul.name = identity.get("name", soul_folder_name.capitalize())
        soul.archetype = identity.get("archetype", "Standard")
        soul.gender = identity.get("gender", "Unknown")
        soul.age = identity.get("age", 0)
        soul.version = core_data.get("meta", {}).get("version", "1.5.2")

        # 2. STITCH THE 6 PILLARS 
        soul.identity_data = identity
        soul.appearance_data = core_data.get("appearance", {})
        soul.personality_data = core_data.get("personality", {})
        
        soul.social_engine = {
            "intimacy_behavior": core_data.get("intimacy_behavior", {}),
            "behavioral_filters": metadata_data.get("behavioral_filters", {}),
            "memory_schema": metadata_data.get("memory_schema", {})
        }
        
        soul.world_presence = context_data.get("world_presence", {})
        
        soul.system_config = {
            "multimodal_hooks": core_data.get("multimodal_hooks", {}),
            "technical_metadata": metadata_data.get("technical_metadata", {}),
            "event_hooks": context_data.get("event_hooks", {})
        }

        session.add(soul)
        session.commit()
        print(f"✅ Loaded: {soul.name}")

def batch_import_all_souls():
    """
    The Master Loop: Crawls the /souls/ directory.
    “I’m looking for a few good men… or souls.”
    """
    souls_root = "souls"
    
    if not os.path.exists(souls_root):
        print(f"❌ Root folder '{souls_root}' not found!")
        return

    # Get all items in /souls/ that are actually directories
    soul_folders = [f for f in os.listdir(souls_root) if os.path.isdir(os.path.join(souls_root, f))]
    
    print(f"🗂️  Found {len(soul_folders)} soul candidates. Starting ingestion...")

    for folder in soul_folders:
        import_soul_from_folder(folder)

    print("\n🏁 All souls have been synchronized with Link City.")

if __name__ == "__main__":
    batch_import_all_souls()