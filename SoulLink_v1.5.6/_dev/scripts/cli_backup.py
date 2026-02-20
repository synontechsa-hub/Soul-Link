# /_dev/scripts/cli_backup.py
# Normandy-SR2 — Standalone Backup CLI
# "The record remains. Your path is preserved."

import asyncio
import sys
import os

# Add project root to path so we can import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.services.backup_service import BackupService
from backend.app.core.logging_config import setup_logging

async def run_backup():
    print("🚀 Initializing Legion Backup Sequence...")
    setup_logging()
    
    try:
        archive_path = await BackupService.perform_full_backup()
        if archive_path:
            print(f"✅ Backup Successful: {archive_path}")
        else:
            print("⚠️ Backup complete, but no new archive was generated (check logs).")
    except Exception as e:
        print(f"❌ Backup FAILED: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_backup())
