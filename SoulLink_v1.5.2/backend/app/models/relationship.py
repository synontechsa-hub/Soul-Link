# /backend/app/models/relationship.py
# /version.py
# /_dev/

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

# “Connection is the energy that exists between people.”
# - Brené Brown

class SoulRelationship(SQLModel, table=True):
    __tablename__ = "user_soul_relationships"
    
    # Composite Primary Key: One entry per User-Soul pair
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    soul_id: str = Field(index=True)
    
    # Intimacy Metrics (The core of SoulLink)
    intimacy_score: int = Field(default=0)
    current_tier: str = Field(default="STRANGER")
    
    current_location: str = Field(default="linkview_cuisine")
    # High-Fidelity Trackers (Rosalynn/Adrian specifics)
    # “Trust is like a mirror, you can fix it if it's broken, 
    # but you can still see the crack in that motherf*cker's reflection.”
    # - Lady Gaga (probably not, but it fits the vibe)
    propriety_level: int = Field(default=100) 
    trust_score: int = Field(default=0)
    
    # Milestone Trackers
    met_at: datetime = Field(default_factory=datetime.utcnow)
    last_interaction: datetime = Field(default_factory=datetime.utcnow)

    # Multi-Soul logic (for the v1.1.0 hybrid system)
    is_active_link: bool = Field(default=True)

    