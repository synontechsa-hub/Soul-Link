# /backend/app/models/user_persona.py
# v1.5.6 Identity Layer - The Masks We Wear

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, UniqueConstraint
from datetime import datetime
from typing import Optional, Dict, Any

class UserPersona(SQLModel, table=True):
    """
    The Identity Layer.
    Allows a single User Account to have multiple "Masks" or personas.
    Souls perceive the user through the ACTIVE persona only.
    """
    __tablename__ = "user_personas"
    
    # Core Identifiers
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.user_id", index=True, max_length=36)
    
    # Identity Data
    screen_name: str = Field(max_length=50)
    bio: Optional[str] = Field(default=None, max_length=500)
    age: Optional[int] = Field(default=None)
    gender: Optional[str] = Field(default=None, max_length=20)
    
    # The Identity Anchor (v1.5.6 feature)
    # A seemingly small detail that Souls fixate on to recognize "You" across personas.
    # e.g., "Always wears a specific ring", "Smells like ozone"
    identity_anchor: Optional[str] = Field(default=None, max_length=200)
    
    # State
    is_active: bool = Field(default=False, description="Only one persona per user can be active at a time")
    
    # Meta
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata for frontend specific settings (avatar, theme color, etc)
    meta_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
