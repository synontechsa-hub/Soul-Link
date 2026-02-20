import os
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import async_session_maker
from backend.app.models.user import User
from backend.app.models.soul import Soul, SoulState
from backend.app.models.location import Location
from backend.app.models.link_state import LinkState
from backend.app.models.user_persona import UserPersona
from backend.app.models.conversation import Conversation

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

            # Perform each table backup in its own session block to isolate failures
            await BackupService._safe_backup(User, "users", timestamp)
            await BackupService._safe_backup(Soul, "souls", timestamp)
            await BackupService._safe_backup(LinkState, "link_states", timestamp)
            await BackupService._safe_backup(UserPersona, "user_personas", timestamp)
            await BackupService._safe_backup(Location, "locations", timestamp)
            await BackupService._safe_backup(Conversation, "conversations", timestamp)
            
            logger.info(f"✅ Backup Complete! ({timestamp})")
            
            # Prune old backups
            await BackupService._prune_backups(keep_last=10)
            
        except Exception as e:
            logger.error(f"❌ Backup Failed: {e}", exc_info=True)
            # We don't raise here to avoid crashing the server on optional background tasks
            # but we definitely log it.

    @staticmethod
    async def _safe_backup(model, name: str, timestamp: str):
        """Wraps _backup_table in a session and try/except to isolate failures."""
        try:
            async with async_session_maker() as session:
                await BackupService._backup_table(session, model, name, timestamp)
        except Exception as e:
            logger.error(f"❌ Failed to backup {name}: {e}")

    @staticmethod
    async def _backup_table(session: AsyncSession, model, name: str, timestamp: str):
        try:
            result = await session.execute(select(model))
            records = result.scalars().all()
            
            # Use model_dump for Pydantic v2/SQLModel compatibility
            data = [record.model_dump(mode='json') if hasattr(record, 'model_dump') else str(record) for record in records]
            
            filename = f"{name}_{timestamp}.json"
            filepath = BACKUP_DIR / filename
            
            # Write to file (NON-BLOCKING via Executor)
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, BackupService._write_json, filepath, data)
                
            logger.info(f"📦 Saved {len(data)} {name}")
            
        except Exception as e:
            # Re-raise to be caught by _safe_backup
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
