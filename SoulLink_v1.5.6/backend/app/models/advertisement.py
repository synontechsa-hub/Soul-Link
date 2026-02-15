# /backend/app/models/advertisement.py
# /version.py v1.5.6 Normandy SR-2

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class AdEvent(SQLModel, table=True):
    """
    Tracks advertisement viewing events for analytics and reward validation.
    Used to monitor ad performance and prevent fraud.
    """
    __tablename__ = "ad_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.user_id", max_length=36)
    
    # Ad Classification
    ad_type: str = Field(max_length=20)
    # Options: "rewarded_video", "interstitial", "banner", "billboard"
    
    ad_provider: str = Field(max_length=20, default="admob")
    # Options: "admob", "unity_ads", "applovin"
    
    # Tracking
    watched_at: datetime = Field(default_factory=datetime.utcnow)
    completed: bool = Field(default=False)  # Did they watch the full ad?
    
    # Reward Details
    reward_type: Optional[str] = Field(default=None, max_length=20)
    # Options: "stability", "overdrive", "gems", None (for interstitials)
    
    reward_amount: int = Field(default=0)
    # For stability: 25, for overdrive: 600 (10 min in seconds), for gems: varies
    
    # Context
    trigger_location: Optional[str] = Field(default=None, max_length=50)
    # Where was the ad triggered? "apartment_tv", "map_billboard", "bed_transition", "boot_sequence"
