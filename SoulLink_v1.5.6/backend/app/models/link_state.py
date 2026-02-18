# /backend/app/models/link_state.py
# v1.5.6 Mirror System - The User's Mirror to the Soul

from sqlmodel import SQLModel, Field, Column
from pydantic import BaseModel
from sqlalchemy import JSON, UniqueConstraint
from datetime import datetime
from typing import Optional, Dict, Any

class LinkState(SQLModel, table=True):
    """
    The unified mutable state between a User and a Soul.
    Consolidates Intimacy (Relationship) and Stability (Monetization).
    Acts as the "Writable Mirror" to the "Read-Only Soul Blueprint".
    """
    __tablename__ = "link_states"
    __table_args__ = (UniqueConstraint("user_id", "soul_id", name="uq_link_state_user_soul"),)

    # Core Identifiers
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=36)
    soul_id: str = Field(index=True, max_length=50)

    # --- 1. THE VOLATILE MIRROR (Reassignment from SoulState) ---
    current_mood: str = Field(default="neutral", max_length=50)
    current_location: Optional[str] = Field(default=None, max_length=50, description="Override location for this user only")
    energy_pool: int = Field(default=100, description="User-specific energy interaction pool")
    
    # --- 2. THE INTIMACY LADDER (From Relationship) ---
    intimacy_score: int = Field(default=0)
    intimacy_tier: str = Field(default="STRANGER", max_length=20)
    
    # --- 3. THE MASK (New v1.5.6 Mechanic) ---
    mask_integrity: float = Field(default=1.0, description="1.0 = Full Persona, 0.0 = Raw Soul/Glitch")
    
    # --- 4. THE MONETIZATION SIGNAL (From UserSoulState) ---
    signal_stability: float = Field(default=100.0, description="Degrades with interaction, restored by Ad/Gem")
    last_stability_decay: datetime = Field(default_factory=datetime.utcnow)
    
    # --- 5. PERMISSIONS & GATES ---
    unlocked_nsfw: bool = Field(default=False)
    is_architect: bool = Field(default=False)
    
    # --- METADATA ---
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_interaction: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # Flags for specific mechanics (e.g. "Glove Removed", "True Name Known")
    flags: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))

    # --- STATS ---
    total_messages_sent: int = Field(default=0, description="Total messages exchanged in this link")

class LinkStateRead(BaseModel):
    soul_id: str
    intimacy_tier: str
    current_mood: str
    mask_integrity: float
    signal_stability: float
