# /backend/app/models/lore_item.py
# v1.5.5 Domain Expansion - Lore System

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Text
from typing import Dict, List, Optional
from datetime import datetime

class LoreItem(SQLModel, table=True):
    """
    KNOWLEDGE BASE ITEM
    A discrete chunk of world lore that can be retrieved by the LLM
    based on topics, location, or soul associations.
    """
    __tablename__ = "lore_items"

    id: str = Field(primary_key=True, max_length=100)
    category: str = Field(max_length=50) # history, faction, event, entity
    
    # search tags for vector-like retrieval
    topics: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # The actual content, gated by clearance level
    # { "common": "...", "rare": "...", "secret": "..." }
    content: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Links to other entities
    # { "related_souls": [], "related_factions": [] }
    associations: Dict[str, List[str]] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Metadata for provenance
    source_metadata: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))
    
    version: str = Field(default="1.5.5", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
