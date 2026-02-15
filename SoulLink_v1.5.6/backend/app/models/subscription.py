# /backend/app/models/subscription.py
# /version.py v1.5.6 Normandy SR-2

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class SubscriptionHistory(SQLModel, table=True):
    """
    Tracks subscription lifecycle events for billing and analytics.
    Maintains historical record of all subscription changes.
    """
    __tablename__ = "subscription_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.user_id", max_length=36)
    
    # Subscription Details
    tier: str = Field(max_length=20)
    # Options: "soul_seeker", "soul_master", "architect"
    
    status: str = Field(max_length=20)
    # Options: "active", "cancelled", "expired", "trial", "refunded"
    
    # Lifecycle
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    
    # Payment Details
    payment_provider: str = Field(default="stripe", max_length=20)
    # Options: "stripe", "paypal", "apple_iap", "google_play"
    
    transaction_id: Optional[str] = Field(default=None, max_length=100)
    
    amount_paid: float = Field(default=0.0)
    currency: str = Field(default="USD", max_length=3)
    
    # Metadata
    cancellation_reason: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None, max_length=500)
