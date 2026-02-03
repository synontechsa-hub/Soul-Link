# /backend/app/models/relationship.py
# /version.py
# /_dev/

# "War, war never changes."
# - Fallout
from sqlmodel import SQLModel, Field, Column
from pydantic import BaseModel
from sqlalchemy import JSON, UniqueConstraint
from datetime import datetime
from typing import Optional, Dict, Any

# "Had to be me. Someone else might have gotten it wrong."
# - Mordin Solus - Mass Effect
class SoulRelationship(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "soul_id", name="uq_user_soul"),)
    """
    Tracks the bond between a specific User and a Soul.
    Handles intimacy progression, location state, and special flags.
    """
    __tablename__ = "user_soul_relationships"

    relationship_id: Optional[int] = Field(default=None, primary_key=True)

    # Core linkage
    # Ensure foreign_key="users.user_id" matches your actual User model table name
    user_id: str = Field(
        index=True,
        max_length=36 
    )
    soul_id: str = Field(
        index=True,
        max_length=50
    )

    # Intimacy system
    intimacy_score: int = Field(default=0)
    intimacy_tier: str = Field(
        default="STRANGER",
        max_length=20,
        description="STRANGER | TRUSTED | SOUL_LINKED"
    )

    # Current world state
    current_location: Optional[str] = Field(
        default="linkgate_mall", # Default starting point
        max_length=50
    )

    # Soul-specific flags (curse progress, glove status, etc.)
    # We use Dict[str, Any] to match your Soul model pillar style
    special_flags: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON)
    )

    # 🚀 RECOGNITION & CONTENT GATING 🚀
    # Set to True only if user matches the dev_config during first link or via admin
    is_architect: bool = Field(default=False)
    
    # Decides if NSFW content is active for this specific pairing
    nsfw_unlocked: bool = Field(default=False)

    # "Don't be sorry, be better."
    # - Kratos - God of War
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_interaction: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

# --- READ SCHEMAS (For API Responses) ---
class RelationshipRead(BaseModel):
    soul_id: str
    intimacy_tier: str
    current_location: str
    is_architect: bool
    nsfw_unlocked: bool
    last_interaction: datetime