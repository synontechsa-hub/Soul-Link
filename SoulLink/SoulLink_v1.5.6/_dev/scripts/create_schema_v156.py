from backend.app.models import (
    Soul, SoulPillar, SoulState,
    Location,
    User,
    Conversation,
    TimeSlot,
    AdImpression,
    LoreItem,
    LinkState,
    SoulMemory,
    UserPersona,
    UserProgress,
    SystemConfig,
)
from backend.app.database.session import engine
from sqlmodel import SQLModel
import sys
import os

sys.path.insert(0, r"d:\Coding\SynonTech\SoulLink\SoulLink_v1.5.6")


# Import ALL models so SQLModel registers them for create_all()


def create_schema():
    print("Creating v1.5.6 schema (fresh database only)...")
    print("NOTE: For existing databases, use: alembic upgrade head")
    try:
        SQLModel.metadata.create_all(engine)
        print("All tables created successfully.")

        # List what was created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\nTables in DB ({len(tables)}):")
        for t in sorted(tables):
            print(f"   - {t}")
    except Exception as e:
        print(f"Schema creation failed: {e}")
        raise


if __name__ == "__main__":
    create_schema()
