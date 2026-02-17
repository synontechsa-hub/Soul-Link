# /backend/app/models/soul_memory.py
# v1.5.6 Long-Term Narrative Storage (The Notebook)

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Text
from datetime import datetime
from typing import Optional, List, Dict, Any

class SoulMemory(SQLModel, table=True):
    """
    The persistent narrative history between User and Soul.
    Optimized for RAG (Retrieval Augmented Generation) context injection.
    Separated from LinkState to avoid loading massive text blobs on every tick.
    """
    __tablename__ = "soul_memories"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Owning LinkState (One-to-One)
    link_state_id: int = Field(foreign_key="link_states.id", index=True)
    
    # --- THE NOTEBOOK ---
    # A concise, LLM-generated summary of the entire relationship history ("Pre-context")
    summary: str = Field(default="", sa_column=Column(Text))
    
    # --- FACTUAL KEY-VALUE STORE ---
    # Specific verified facts (e.g., {"user_job": "Architect", "favorite_color": "Blue"})
    facts: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # --- MILESTONE TRACKER ---
    # List of "Canon Events" completed (e.g., ["first_kiss", "secret_revealed_01"])
    milestones: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)
