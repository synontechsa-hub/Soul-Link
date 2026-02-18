"""
create_schema_v156.py
Creates all v1.5.6 tables directly using SQLModel.metadata.create_all().
Use this instead of Alembic when starting from a completely empty database.

Usage:
    python create_schema_v156.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlmodel import SQLModel
from backend.app.database.session import engine

# Import ALL models so SQLModel registers them for create_all()
from backend.app.models import (
    Soul, SoulPillar, SoulState,
    Location,
    User,
    SoulRelationship,
    Conversation,
    TimeSlot,
    UserSoulState,
    AdImpression,
    LoreItem,
    LinkState,
    SoulMemory,
    UserPersona,
    UserProgress,
)

def create_schema():
    print("🏗️  Creating v1.5.6 schema...")
    try:
        SQLModel.metadata.create_all(engine)
        print("✅ All tables created successfully.")
        
        # List what was created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n📋 Tables in DB ({len(tables)}):")
        for t in sorted(tables):
            print(f"   - {t}")
    except Exception as e:
        print(f"❌ Schema creation failed: {e}")
        raise

if __name__ == "__main__":
    create_schema()
