
import json
import sys
import os
from pathlib import Path
from sqlalchemy import text
from sqlmodel import Session, SQLModel

# Path setup
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database.session import engine
from backend.app.models import Soul, Location, SoulRelationship, Conversation, User

BACKUP_DIR = project_root / "_dev" / "data_backups"

def get_latest_timestamp():
    """Finds the timestamp of the most recent backup set."""
    timestamps = set()
    for f in BACKUP_DIR.glob("*.json"):
        parts = f.stem.split('_')
        if len(parts) >= 3:
            ts = f"{parts[-2]}_{parts[-1]}"
            timestamps.add(ts)
    
    if not timestamps:
        return None
    return sorted(list(timestamps))[-1]

def restore_table(session: Session, model, name: str, timestamp: str):
    """Restores a single table from JSON."""
    filename = f"{name}_{timestamp}.json"
    filepath = BACKUP_DIR / filename
    
    if not filepath.exists():
        print(f"⚠️  Backup file not found: {filename}. Skipping.")
        return

    print(f"📥 Restoring {name} from {filename}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        count = 0
        for record_data in data:
            # Create instance from dict (validate with model)
            instance = model.model_validate(record_data)
            session.add(instance)
            count += 1
            
        print(f"✅ Loaded {count} records into {name}")
    except Exception as e:
        print(f"❌ Failed to restore {name}: {e}")
        raise e

def clear_tables(session: Session):
    """Truncates tables in reverse dependency order."""
    print("🧹 Clearing existing data...")
    # Order matters: Child -> Parent
    session.exec(text("DELETE FROM conversations"))
    session.exec(text("DELETE FROM soul_relationships"))
    session.exec(text("DELETE FROM souls"))
    session.exec(text("DELETE FROM locations")) # locations might be referenced by souls
    session.exec(text("DELETE FROM users"))
    session.commit()
    print("✅ Tables cleared.")

def run_restore(timestamp=None):
    if not BACKUP_DIR.exists():
        print(f"❌ Backup directory not found: {BACKUP_DIR}")
        return

    if not timestamp:
        timestamp = get_latest_timestamp()
        if not timestamp:
            print("❌ No backups found.")
            return
        print(f"ℹ️  Using latest backup: {timestamp}")
    else:
        print(f"ℹ️  Using specified backup: {timestamp}")

    print(f"🚀 Starting Database Restore ({timestamp})...\n")

    with Session(engine) as session:
        # 1. Clear Data
        try:
            clear_tables(session)
        except Exception as e:
             print(f"❌ Failed to clear tables: {e}")
             return

        # 2. Restore in Dependency Order (Parent -> Child)
        try:
            restore_table(session, User, "users", timestamp)
            restore_table(session, Location, "locations", timestamp)
            restore_table(session, Soul, "souls", timestamp)
            restore_table(session, SoulRelationship, "relationships", timestamp)
            restore_table(session, Conversation, "conversations", timestamp)
            
            session.commit()
            print("\n✨ Restore complete! The timeline has been reset.")
            
        except Exception as e:
            session.rollback()
            print(f"\n❌ CRITICAL: Restore failed. Transaction rolled back. Error: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Restore database from JSON backup.")
    parser.add_argument("--timestamp", help="Specific timestamp to restore (YYYYMMDD_HHMMSS). Defaults to latest.")
    args = parser.parse_args()
    
    run_restore(args.timestamp)
