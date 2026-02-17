# /backend/app/models/soul.py
# /version.py
# /_dev/

from typing import Dict, Any
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB

# We change this to SoulBase so the next class can find it!
class SoulBase(SQLModel):
    # Core identifiers
    # “A man chooses, a slave obeys.”
    # - BioShock
    
    # Note: soul_id stays in the final Soul class as the primary key
    name: str = Field(index=True)
    archetype: str
    
    # Quick access fields for searching/filtering
    gender: str
    age: int
    version: str = Field(default="1.5.2")

# “You are not defined by your past, but by the choices you make today.”
# - Mass Effect
class Soul(SoulBase, table=True):
    __tablename__ = "souls"
    
    # The actual Primary Key for the DB
    soul_id: str = Field(primary_key=True)

    # The 6 Pillars of the new Schema
    # “What is a man? A miserable little pile of secrets.” 
    # Castlevania: Symphony of the Night
    identity_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    appearance_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    personality_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    social_engine: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    world_presence: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    system_config: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))