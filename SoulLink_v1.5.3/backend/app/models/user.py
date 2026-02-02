# /backend/app/models/user.py
# /version.py v1.5.3-P

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    user_id: str = Field(primary_key=True, max_length=12)
    username: str = Field(unique=True, max_length=50)
    display_name: Optional[str] = Field(default=None, max_length=100)
    
    # 🏠 APARTMENT / PROFILE DATA (New for v1.5.3-P)
    # This is what the Souls will use to "know" you.
    age: Optional[int] = Field(default=None)
    gender: Optional[str] = Field(default=None, max_length=20)
    bio: Optional[str] = Field(default=None, max_length=500)
    
    # 💎 THE ECONOMY
    account_tier: str = Field(default="free", max_length=20)
    gems: int = Field(default=0)
    
    # ⚡ THE ENERGY SYSTEM (Genius Rate Limiting)
    energy: int = Field(default=100)
    lifetime_tokens_used: int = Field(default=0)
    
    last_ad_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)