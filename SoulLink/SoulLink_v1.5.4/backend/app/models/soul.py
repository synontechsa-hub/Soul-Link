# /backend/app/models/soul.py
# "Does this unit have a soul?" - Legion - Mass Effect 2

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON 
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from version import VERSION_SHORT

# --- THE THREE PILLARS ARCHITECTURE ---

class Soul(SQLModel, table=True):
    """
    CORE IDENTITY PILLAR: The static essence of the soul.
    Unchanging identifiers and visual identity.
    """
    __tablename__ = "souls"

    soul_id: str = Field(primary_key=True, max_length=50)
    name: str = Field(max_length=100)
    summary: str = Field(default="A mysterious soul...")
    portrait_url: str = Field(default="/assets/images/souls/default_01.jpeg")
    archetype: Optional[str] = Field(default=None, max_length=100)
    version: str = Field(default=VERSION_SHORT, max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SoulPillar(SQLModel, table=True):
    """
    LOGIC PILLAR: The heavy definitions that drive consciousness.
    Stored separately to avoid loading massive JSONs during simple lookups.
    """
    __tablename__ = "soul_pillars"

    soul_id: str = Field(primary_key=True, foreign_key="souls.soul_id")
    
    # ⏰ DEFINITION: Routines
    routines: Dict[str, str] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Time slot -> location_id mapping"
    )

    # 🧬 DEFINITION: The Pillars
    identity_pillar: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    aesthetic_pillar: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    interaction_engine: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))

    # 🚀 DEFINITION: Overrides & Meta
    llm_instruction_override: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    meta_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    personality: Optional[str] = Field(default=None, max_length=2000)

class SoulState(SQLModel, table=True):
    """
    STATE PILLAR: The hot, frequently updated live data.
    Optimized for rapid writes (location, energy, mood).
    """
    __tablename__ = "soul_states"

    soul_id: str = Field(primary_key=True, foreign_key="souls.soul_id")
    current_location_id: str = Field(default="soul_plaza", max_length=100)
    energy: int = Field(default=100)
    mood: str = Field(default="neutral", max_length=50)
    
    # Dynamic logic states from Interaction Engine
    anxiety_level: int = Field(default=0)
    performance_mode: int = Field(default=100)
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# --- READ MODELS (Frontend Aggregates) ---

class SoulRead(BaseModel):
    """Combined view for the frontend to digest."""
    soul_id: str
    name: str
    summary: str
    portrait_url: str
    archetype: Optional[str]
    version: str
    
    # Live data enrichment
    current_location_id: str
    energy: int
    mood: str
    
    # Key pillars for UI rendering (e.g. signature emotes)
    aesthetic_pillar: Dict[str, Any]
