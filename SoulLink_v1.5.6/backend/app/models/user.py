# /backend/app/models/user.py
# /version.py v1.5.6 Normandy SR-2

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    __tablename__ = "users"

    # ────────────────────────────────────────────────────────────────
    #   IDENTITY
    # ────────────────────────────────────────────────────────────────
    # Matches Supabase Auth UUID
    user_id: str = Field(primary_key=True, max_length=36)

    username: Optional[str] = Field(default=None, max_length=50)
    display_name: Optional[str] = Field(default=None, max_length=100)

    # Updated on every authenticated request. Used by Chronicle time-jump logic.
    last_seen_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # ────────────────────────────────────────────────────────────────
    #   PROFILE (Mirror — what Souls know about you)
    # ────────────────────────────────────────────────────────────────
    age: Optional[int] = Field(default=None)
    gender: Optional[str] = Field(default=None, max_length=20)
    bio: Optional[str] = Field(default=None, max_length=1000)

    # ────────────────────────────────────────────────────────────────
    #   ECONOMY
    # ────────────────────────────────────────────────────────────────
    account_tier: str = Field(default="free", max_length=20)
    # Options: "free", "premium", "architect"

    gems: int = Field(default=0)
    energy: int = Field(default=100)
    lifetime_tokens_used: int = Field(default=0)

    last_energy_refill: datetime = Field(default_factory=datetime.utcnow)
    last_ad_at: Optional[datetime] = Field(default=None)
    ad_cooldown_until: Optional[datetime] = Field(default=None)
    stability_overdrive_until: Optional[datetime] = Field(default=None)
    total_ads_watched: int = Field(default=0)

    # ────────────────────────────────────────────────────────────────
    #   SUBSCRIPTION (v1.5.6 — Quantum Link Premium)
    # ────────────────────────────────────────────────────────────────
    subscription_status: Optional[str] = Field(default=None, max_length=20)
    # Options: None | "active" | "cancelled" | "expired" | "trial"
    subscription_start: Optional[datetime] = Field(default=None)
    subscription_end: Optional[datetime] = Field(default=None)
    stripe_customer_id: Optional[str] = Field(default=None, max_length=100)
    stripe_subscription_id: Optional[str] = Field(default=None, max_length=100)

    # ────────────────────────────────────────────────────────────────
    #   WORLD STATE — per-user, fully isolated
    # ────────────────────────────────────────────────────────────────
    current_location: str = Field(default="linkside_apartment", max_length=50)

    # Time slot (turn-based progression)
    current_time_slot: str = Field(default="morning", max_length=20)
    # Options: "morning" | "afternoon" | "evening" | "night" | "home_time"

    # In-game calendar — drives season + weather per user
    # Advances on sleep (home_time slot). See calendar.json + weather.json.
    calendar_day: int = Field(default=1)        # 1–30
    calendar_month: int = Field(default=1)      # 1–12 → maps to season
    calendar_year: int = Field(default=1)

    # Derived from calendar_month — cached here to avoid recalculation every request.
    # Updated by WeatherService on each day advance.
    current_season: str = Field(default="frostlink", max_length=20)
    # Options: "frostlink" | "surgespring" | "burnseason" | "shadowfall"

    # Set once per in-game day via WeatherService weighted random from weather.json.
    # Persists until the next sleep cycle. Every user has their own weather.
    current_weather: str = Field(default="clear_frost", max_length=50)

    # ────────────────────────────────────────────────────────────────
    #   PROGRESSION
    # ────────────────────────────────────────────────────────────────
    total_sessions: int = Field(default=0)
    total_messages_sent: int = Field(default=0)
    # Increments on each day advance
    total_days_played: int = Field(default=0)
    # Count of SOUL_LINKED tier relationships
    souls_linked: int = Field(default=0)

    # ────────────────────────────────────────────────────────────────
    #   SETTINGS (server-side, synced across devices)
    # ────────────────────────────────────────────────────────────────
    # Server enforces NSFW gate — requires age >= 18 AND explicit opt-in.
    # Client cannot override this.
    nsfw_enabled: bool = Field(default=False)
    notifications_enabled: bool = Field(default=True)
    language: str = Field(default="en", max_length=10)
