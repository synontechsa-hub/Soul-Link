# /backend/app/models/user.py
# /version.py
# /_dev/

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    # Primary Identifiers
    user_id: str = Field(primary_key=True)
    username: str = Field(index=True, unique=True)
    display_name: Optional[str] = None
    account_tier: str = Field(default="free")
    
    # Silent Resource Management
    # This is the 'Energy' users don't see
    energy: int = Field(default=100) 
    ad_grants_this_week: int = Field(default=0)
    lifetime_tokens_used: int = Field(default=0)
    
    # Timing
    last_chat_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)