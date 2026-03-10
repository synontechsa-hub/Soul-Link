import os
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import async_session_maker
from backend.app.models import Soul, Location, SoulRelationship, Conversation, User

logger = logging.getLogger("System.Backup")

BACKUP_DIR = Path(__file__).resolve().parent.parent.parent.parent / "_dev" / "data_backups"

class BackupService:
    @staticmethod
    async def perform_full_backup():
        """
        Exports all critical tables to JSON files in _dev/data_backups.
        Runs asynchronously to avoid blocking the main thread.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"⏳ Starting Database Backup ({timestamp})...")
        
        try:
            if not BACKUP_DIR.exists():
                BACKUP_DIR.mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 Created backup directory: {BACKUP_DIR}")

            async with async_session_maker() as session:
                await BackupService._backup_table(session, User, "users", timestamp)
                await BackupService._backup_table(session, Soul, "souls", timestamp)
                await BackupService._backup_table(session, SoulRelationship, "relationships", timestamp)
                await BackupService._backup_table(session, Location, "locations", timestamp)
                await BackupService._backup_table(session, Conversation, "conversations", timestamp)
            
            logger.info(f"✅ Backup Complete! ({timestamp})")
            
            # Prune old backups
            await BackupService._prune_backups(keep_last=10)
            
        except Exception as e:
            logger.error(f"❌ Backup Failed: {e}", exc_info=True)
            raise e

    @staticmethod
    async def _backup_table(session: AsyncSession, model, name: str, timestamp: str):
        try:
            result = await session.execute(select(model))
            records = result.scalars().all()
            
            data = [record.model_dump(mode='json') for record in records]
            
            filename = f"{name}_{timestamp}.json"
            filepath = BACKUP_DIR / filename
            
            # Write to file (NON-BLOCKING via Executor)
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, BackupService._write_json, filepath, data)
                
            logger.info(f"📦 Saved {len(data)} {name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to backup {name}: {e}")
            raise e

    @staticmethod
    def _write_json(filepath, data):
        """Helper to write JSON in a thread-safe way (run by executor)."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    @staticmethod
    async def _prune_backups(keep_last: int = 10):
        """Keep only the most recent N sets of backups."""
        try:
            backups = {}
            for f in BACKUP_DIR.glob("*.json"):
                # Format: table_YYYYMMDD_HHMMSS.json
                parts = f.stem.split('_')
                if len(parts) >= 3:
                    timestamp = f"{parts[-2]}_{parts[-1]}"
                    if timestamp not in backups:
                        backups[timestamp] = []
                    backups[timestamp].append(f)
            
            sorted_ts = sorted(backups.keys(), reverse=True)
            
            if len(sorted_ts) > keep_last:
                to_delete = sorted_ts[keep_last:]
                logger.info(f"🧹 Pruning {len(to_delete)} old backup sets...")
                
                for ts in to_delete:
                    for f in backups[ts]:
                        f.unlink()
                        
                logger.info("✅ Pruning complete.")
        except Exception as e:
            logger.warning(f"⚠️ Pruning failed: {e}")
