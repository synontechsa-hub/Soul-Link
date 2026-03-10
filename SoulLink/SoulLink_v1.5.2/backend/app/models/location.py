# /backend/app/models/location.py
from typing import Dict, Any, List, Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB

# “Stay awhile and listen.”
# - Deckard Cain - Diablo

class LocationBase(SQLModel):
    display_name: str = Field(index=True)
    category: str  # e.g., 'fine_dining_restaurant'
    description: str
    music_track: str = Field(default="ambient_city_loop.mp3")

# “The night is long, and the city even longer.”
# - Vampire the Masquerade: Bloodlines
class Location(LocationBase, table=True):
    __tablename__ = "locations"
    
    location_id: str = Field(primary_key=True) # 'linkview_cuisine'
    
    # 1.5.2 Architect Pillars for Locations
    # Stores the "Judge/Narrator/Censor" logic
    system_modifiers: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    
    # Stores mood_modifiers (energy, openness, etc.)
    environmental_prompts: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    
    # Minimum intimacy required to enter or see the soul here
    min_intimacy: int = Field(default=0)