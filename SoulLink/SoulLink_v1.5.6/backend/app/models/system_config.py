# /backend/app/models/system_config.py
# /version.py v1.5.6 Normandy SR-2
# /_dev/

# "The right man in the wrong place can make all the difference in the world."
# - G-Man - Half-Life 2

from sqlmodel import SQLModel, Field
from sqlalchemy import JSON, Column
from datetime import datetime, timezone
from backend.app.core.utils import utcnow
from typing import Dict, Any, Optional


class SystemConfig(SQLModel, table=True):
    """
    Key-value store for all system JSON configurations.
    Replaces all _dev/data/system/*.json runtime reads.
    One row per config file. Loaded into memory at startup.
    """
    __tablename__ = "system_config"

    key: str = Field(primary_key=True, max_length=100)
    data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON)
    )
    version: str = Field(default="1.5.6", max_length=20)
    updated_at: datetime = Field(
        default_factory=lambda: utcnow()
    )
