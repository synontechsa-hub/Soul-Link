# /_dev/scripts/backup_db.py
# "Backup is the soul of data stability."

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy import text
from sqlmodel import Session

# Setup project path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database.session import engine
from backend.app.models import Soul, Location, SoulRelationship, Conversation, User

BACKUP_DIR = project_root / "_dev" / "data_backups"

def backup_table(session: Session, model, name: str, timestamp: str):
    """Backup a single table to a JSON file."""
    print(f"📦 Backing up {name}...")
    try:
        # Fetch all records
        results = session.query(model).all()
        data = [record.model_dump(mode='json') for record in results]
        
        filename = f"{name}_{timestamp}.json"
        filepath = BACKUP_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
            
        print(f"✅ Saved {len(data)} records to {filename}")
    except Exception as e:
        print(f"❌ Failed to backup {name}: {e}")

def prune_backups(keep_last: int = 10):
    """Keep only the most recent N sets of backups."""
    print(f"\n🧹 Cleaning up old backups (keeping last {keep_last})...")
    
    # Files are named like "users_20260205_210122.json"
    # We group by the timestamp part
    backups = {}
    for f in BACKUP_DIR.glob("*.json"):
        # Format: table_YYYYMMDD_HHMMSS.json
        parts = f.stem.split('_')
        if len(parts) >= 3:
            timestamp = f"{parts[-2]}_{parts[-1]}"
            if timestamp not in backups:
                backups[timestamp] = []
            backups[timestamp].append(f)
            
    # Sort timestamps newest first
    sorted_ts = sorted(backups.keys(), reverse=True)
    
    if len(sorted_ts) > keep_last:
        to_delete = sorted_ts[keep_last:]
        for ts in to_delete:
            print(f"  🗑️ Removing backup set: {ts}")
            for f in backups[ts]:
                f.unlink()
        print(f"✅ Pruning complete. Removed {len(to_delete)} old backup sets.")
    else:
        print("✅ No pruning needed.")

def run_backup():
    """Main backup orchestration."""
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True)
        print(f"📁 Created backup directory: {BACKUP_DIR}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"🚀 Starting Database Backup ({timestamp})...\n")

    with Session(engine) as session:
        # List of models to backup
        models = [
            (Soul, "souls"),
            (Location, "locations"),
            (SoulRelationship, "relationships"),
            (Conversation, "conversations"),
            (User, "users")
        ]
        
        for model, name in models:
            backup_table(session, model, name, timestamp)

    print(f"\n✨ Backup complete! Files are in {BACKUP_DIR}")
    
    # RUN PRUNING
    prune_backups(keep_last=10)

if __name__ == "__main__":
    run_backup()
