# /import_soul_standard.py
# /version.py
# /_dev/

import json
import os
from sqlmodel import Session, SQLModel, create_engine, select
from backend.app.models.soul import Soul

# 
# === SECURE CONFIGURATION ===
# This pulls the password from terminal environment.
# “We can’t fight change. We can’t fight gravity. We can’t fight nothing.”
# - Dutch van der Linde - Red Dead Redemption
db_password = os.environ.get("SOULLINK_DB_PASS")

if not db_password:
    print("❌ ERROR: 'SOULLINK_DB_PASS' environment variable is not set.")
    print("   Run: export SOULLINK_DB_PASS='yourpassword' in the terminal first.")
    exit(1)

# “You can’t judge us by what we’ve done. Judge us by what we’ve built.”
# - The Boss - Saints Row: The Third
DATABASE_URL = f"postgresql://postgres:{db_password}@localhost:5432/soullink"
engine = create_engine(DATABASE_URL)

# “No one’s destiny is written in stone. We forge our own paths.”
# - Warrior of Light - Final Fantasy XIV: Shadowbringers
def load_json(filepath):
    """Loads JSON and handles the 'uploaded file' wrapper if present"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if "fullContent" in data:
            return data["fullContent"]
        return data

# “No soul is beyond redemption, if only they have the courage to seek it.”
# - Y'shtola - Final Fatasy XIV
def import_soul(folder_path):
    print(f"📂 Scanning folder: {folder_path}...")
    
    try:
        # Load the 3 Pillars of Data
        # The pillars of fate
        core = load_json(os.path.join(folder_path, "core.json"))
        context = load_json(os.path.join(folder_path, "context.json"))
        metadata = load_json(os.path.join(folder_path, "metadata.json"))
    except FileNotFoundError as e:
        print(f"❌ Error: Missing files in {folder_path}\n{e}")
        return

    # Map JSON to the New DB Schema
    # Oh, a mini-map!
    soul_data = Soul(
        soul_id=core["meta"]["id"],
        name=core["identity"]["name"],
        archetype=core["identity"]["archetype"],
        gender=core["identity"]["gender"],
        age=core["identity"]["age"],
        version=core["meta"]["version"],
        
        # Injecting the rich JSON blocks
        # Injections, huh? Count me out!
        identity_data=core["identity"],
        appearance_data={**core["appearance"], **core["multimodal_hooks"], **core["colour_palette"]},
        personality_data=core["personality"],
        social_engine={**core["intimacy_behavior"], **core["consent_model"]},
        world_presence=context["world_presence"],
        system_config=metadata
    )

    # Database Upsert (Insert or Update)
    # “The thing about the past is, it’s always there. You can’t outrun it.”
    # - Michael De Santa - GTA V
    with Session(engine) as session:
        # This checks if the table exists and creates it if missing (using the new schema)
        SQLModel.metadata.create_all(engine) 
        
        # “The world is stranger than we can ever know. But that doesn’t mean we stop looking.”
        # - Jesse Faden - Control
        existing = session.exec(select(Soul).where(Soul.soul_id == soul_data.soul_id)).first()
        if existing:
            print(f"🔄 Overwriting existing soul: {soul_data.name}")
            session.delete(existing)
            session.commit()
        
        # “Time is an unforgiving thing. Once it’s broken, it cannot be fixed.”
        # - Paul Serene - Quantum Break
        session.add(soul_data)
        session.commit()
        print(f"✅ SUCCESS: {soul_data.name} (v{soul_data.version}) Imported Successfully!")

if __name__ == "__main__":
    # Ensure this points to the folder where you put core.json, context.json, etc.

    import_soul("alyssa_data")