# /backend/app/models/location.py
# /version.py
# /_dev/

# "Welcome to Rapture."
# - BioShock
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional

class Location(SQLModel, table=True):
    """
    Legion v1.5.4 Arise Location Schema
    Locations affect soul behavior through system_modifiers
    """
    __tablename__ = "locations"
    
    # Looks like we are actually going pretty deep with the locations
    # Is this not too much for MVP?
    location_id: str = Field(primary_key=True, max_length=50)
    display_name: str = Field(max_length=100)
    category: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None)
    music_track: str = Field(default="ambient_city_loop.mp3", max_length=100)
    
    # Judge/Narrator modifiers (affects soul responses)
    # 🚀 NEW: LEGION OVERRIDES 🚀
    # Stores { "system_anchor": "..." } and specific interaction logic
    system_modifiers: dict = Field(default_factory=dict, sa_column=Column(JSON))
    environmental_prompts: list = Field(default_factory=list, sa_column=Column(JSON))
    
    # For locations with intimacy locks.
    min_intimacy: int = Field(default=0)