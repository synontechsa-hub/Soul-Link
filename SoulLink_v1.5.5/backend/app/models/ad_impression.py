# /backend/app/models/ad_impression.py
# v1.5.5 Monetization Framework

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class AdImpression(SQLModel, table=True):
    """
    Tracks all ad impressions for analytics and revenue optimization.
    Used for:
    - Revenue reporting
    - Fill rate analysis
    - User behavior insights
    - Fraud detection
    """
    __tablename__ = "ad_impressions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # User Context
    user_id: str = Field(foreign_key="users.user_id", max_length=36, index=True)
    
    # Ad Network Details
    ad_network: str = Field(max_length=50, index=True)
    # Options: 'applovin', 'admob', 'tapjoy', 'mock'
    
    ad_type: str = Field(max_length=50)
    # Options: 'rewarded', 'interstitial', 'native', 'banner'
    
    placement: str = Field(max_length=100, index=True)
    # Options: 'apartment_tv', 'stability_boost', 'billboard', 'end_turn'
    
    # Reward Details
    reward_granted: bool = Field(default=False)
    reward_type: Optional[str] = Field(default=None, max_length=50)
    # Options: 'stability_boost', 'energy', 'city_credits', 'gems'
    
    reward_amount: Optional[float] = Field(default=None)
    
    # SSV Validation
    ssv_verified: bool = Field(default=False)
    ssv_signature: Optional[str] = Field(default=None, max_length=255)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    class Config:
        table_args = (
            {"sqlite_autoincrement": True},
        )
