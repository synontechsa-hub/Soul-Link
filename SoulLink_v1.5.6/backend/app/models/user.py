# /backend/app/models/user.py
# /version.py v1.5.6 Normandy SR-2

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    # Matches Supabase UUID
    user_id: str = Field(primary_key=True, max_length=36)
    
    # Guests might not have a username yet
    username: Optional[str] = Field(default=None, max_length=50)
    display_name: Optional[str] = Field(default=None, max_length=100)
    
    # 🏠 APARTMENT / PROFILE DATA (New for v1.5.3-P)
    # This is what the Souls will use to "know" you.
    age: Optional[int] = Field(default=None)
    gender: Optional[str] = Field(default=None, max_length=20)
    bio: Optional[str] = Field(default=None, max_length=1000)
    
    # 💎 THE ECONOMY
    account_tier: str = Field(default="free", max_length=20)
    gems: int = Field(default=0)
    
    # ⚡ THE ENERGY SYSTEM (Genius Rate Limiting)
    energy: int = Field(default=100)
    lifetime_tokens_used: int = Field(default=0)
    
    last_ad_at: Optional[datetime] = None
    last_energy_refill: datetime = Field(default_factory=datetime.utcnow)
    current_location: str = Field(default="linkside_apartment", max_length=50)
    
    # ⏰ TIME SLOT SYSTEM (Turn-Based Progression)
    current_time_slot: str = Field(default="morning", max_length=20)
    
    # 💎 SUBSCRIPTION SYSTEM (v1.5.6 Framework)
    subscription_status: Optional[str] = Field(default=None, max_length=20)
    # Options: None, "active", "cancelled", "expired", "trial"
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    
    # 📺 ADVERTISEMENT TRACKING (v1.5.6 Framework)
    total_ads_watched: int = Field(default=0)
    ad_cooldown_until: Optional[datetime] = None  # Prevent ad spam
    
    # ⚡ STABILITY OVERDRIVE (Billboard Bonus - v1.5.6)
    stability_overdrive_until: Optional[datetime] = None  # 10 min infinite tokens
    
    # 💳 PAYMENT PROVIDER IDs (Future Stripe Integration)
    stripe_customer_id: Optional[str] = Field(default=None, max_length=100)
    stripe_subscription_id: Optional[str] = Field(default=None, max_length=100)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)