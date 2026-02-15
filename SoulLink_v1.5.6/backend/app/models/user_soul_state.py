# /backend/app/models/user_soul_state.py
# v1.5.5 Monetization Framework

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class UserSoulState(SQLModel, table=True):
    """
    Tracks per-soul state for each user, including:
    - Signal stability (monetization mechanic)
    - NSFW preferences (ad safety)
    - Last interaction timestamps
    """
    __tablename__ = "user_soul_state"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Foreign Keys
    user_id: str = Field(foreign_key="users.user_id", max_length=36, index=True)
    soul_id: str = Field(max_length=50, index=True)
    
    # 📡 SIGNAL STABILITY SYSTEM
    # Decays with each message, restored via ads or premium
    signal_stability: float = Field(default=100.0)  # 0-100
    last_stability_decay: datetime = Field(default_factory=datetime.utcnow)
    
    # 💖 INTIMACY SYSTEM (v1.5.5)
    intimacy_score: int = Field(default=0)
    current_tier: str = Field(default="STRANGER", max_length=50)
    
    # 🔞 NSFW PREFERENCES (Ad Safety)
    # When enabled, ads are disabled for this specific soul's chat
    nsfw_enabled: bool = Field(default=False)
    
    # 📊 ANALYTICS
    total_messages_sent: int = Field(default=0)
    total_stability_boosts: int = Field(default=0)
    
    # ⏰ TIMESTAMPS
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        # Ensure unique constraint on (user_id, soul_id)
        table_args = (
            {"sqlite_autoincrement": True},
        )
