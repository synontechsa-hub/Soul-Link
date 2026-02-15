# /_dev/scripts/nuke_db.py
import sys
import os
from pathlib import Path

# Path setup
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import SQLModel
from sqlalchemy import text
from backend.app.core.config import settings
from backend.app.database.session import engine

# Import all models so SQLModel knows what to drop
from backend.app.models.soul import Soul, SoulPillar, SoulState
from backend.app.models.location import Location
from backend.app.models.user import User
from backend.app.models.relationship import SoulRelationship
from backend.app.models.conversation import Conversation

def nuke():
    print("🧨 RAZING THE CITY: Initiating Neural Purge...")
    try:
        # If we are on Postgres, we might need a more aggressive drop
        if settings.database_url.startswith("postgresql"):
            with engine.connect() as conn:
                print("🐘 Postgres detected: Using CASCADE drop...")
                # We drop the public schema and recreate it to ensure everything is gone
                conn.execute(text("DROP SCHEMA public CASCADE;"))
                conn.execute(text("CREATE SCHEMA public;"))
                conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
                conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
                conn.commit()
        else:
            SQLModel.metadata.drop_all(engine)
            
        print("✅ The old world is gone. The slate is clean.")
    except Exception as e:
        print(f"❌ NUKE FAILED: {e}")
        print("💡 Tip: Ensure no other connections (like your terminal or dev server) are active.")

if __name__ == "__main__":
    nuke()