# /backend/app/models/soul.py
# /version.py
# /_dev/

# "Does this unit have a soul?"
# - Legion - Mass Effect 2
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON 
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from version import VERSION_SHORT

# "Your soul is mine!"
# - Shang Tsung - Mortal Kombat
class Soul(SQLModel, table=True):
    __tablename__ = "souls"

    soul_id: str = Field(primary_key=True, max_length=50)
    name: str = Field(max_length=100)
    summary: str = Field(default="A mysterious soul...")

    # 🖼️ NEW: The direct link to your Stable Diffusion output
    # Defaulting to your naming convention: /assets/images/souls/{id}_01.jpeg
    portrait_url: str = Field(default="/assets/images/souls/default_01.jpeg")

    # 📍 The Seeder is looking for this exact line:
    spawn_location: str = Field(default="soul_plaza", max_length=100)

    # The Pillars (Legion structure) — stored as JSON
    identity_pillar: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON)
    )
    aesthetic_pillar: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON)
    )
    interaction_engine: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON)
    )

    # 🚀 NEW: LEGION OVERRIDES 🚀
    # Stores { "system_anchor": "..." } and specific interaction logic
    llm_instruction_override: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Stores system_anchor and instruction overrides"
    )
    
    # Stores content_rating, capabilities, and the CRITICAL dev_config for Syn
    meta_data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Stores ratings, capabilities, and Architect recognition logic"
    )

    # Personality summary for quick LLM prompt injection
    personality: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Concise personality summary / core lore for Brain to read"
    )

    # Metadata
    # "The past is a ghost, the future a dream. All we ever have is now."
    # - Bill Watterson (Calvin and Hobbes)
    version: str = Field(default=VERSION_SHORT, max_length=20)
    archetype: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SoulRead(BaseModel):
    soul_id: str
    name: str
    summary: str
    version: str
    archetype: Optional[str]
    portrait_url: str  # ✅ Now the frontend knows exactly what to load
    aesthetic_pillar: Dict[str, Any]
    spawn_location: str  # ✅ Add this so the Map knows where they start