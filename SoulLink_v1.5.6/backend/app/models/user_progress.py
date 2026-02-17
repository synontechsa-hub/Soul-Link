# /backend/app/models/user_progress.py
# v1.5.6 Gamification Layer - The Hero's Journey

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, List, Dict, Any

class UserProgress(SQLModel, table=True):
    """
    The Progress Layer.
    Tracks achievements, lore unlocks, and global stats across ALL personas.
    This data is tied to the User Account, not the specific Persona.
    """
    __tablename__ = "user_progress"
    
    # Core Identifiers
    user_id: str = Field(primary_key=True, foreign_key="users.user_id", max_length=36)
    
    # 🏆 ACHIEVEMENTS
    # List of unlocked achievement IDs (e.g. ["first_link", "survived_glitch"])
    unlocked_achievements: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # 📜 LORE LIBRARY
    # List of unlocked LoreItem IDs (e.g. ["history_of_architect", "weather_data_rain"])
    unlocked_lore: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # 🗺️ EXPLORATION
    # List of Location IDs visited
    visited_locations: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # 👥 SOCIAL GRAPH
    # List of Soul IDs encountered
    encountered_souls: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # 📊 GLOBAL STATS
    total_messages_sent: int = Field(default=0)
    total_days_active: int = Field(default=0)
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)
