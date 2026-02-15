import pytest
import os
from pathlib import Path
from backend.app.services.backup_service import BackupService, BACKUP_DIR

@pytest.mark.asyncio
async def test_backup_service_execution():
    """Verify that BackupService creates files."""
    
    # 1. Clean up old backups for this test (optional, but good for isolation)
    # We won't delete everything, just check count before/after
    
    initial_count = len(list(BACKUP_DIR.glob("*.json"))) if BACKUP_DIR.exists() else 0
    
    # 2. Run Backup
    await BackupService.perform_full_backup()
    
    # 3. Verify files created
    assert BACKUP_DIR.exists()
    current_count = len(list(BACKUP_DIR.glob("*.json")))
    
    assert current_count > initial_count, "Backup service should have created new files"
    
    # Check for specific files
    users_backup = list(BACKUP_DIR.glob("users_*.json"))
    assert len(users_backup) > 0
    
    print(f"\n✅ Backup Service verified. Created {current_count - initial_count} files in {BACKUP_DIR}")
