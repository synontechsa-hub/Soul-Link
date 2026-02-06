# /backend/app/logic/tier_manager.py
# /version.py v1.5.4 Arise

"""
Tier Benefits Manager
Defines and enforces premium tier benefits for the Link Stability system.
"""

from typing import Dict, Any
from backend.app.models.user import User

# Tier benefit configuration
TIER_BENEFITS = {
    "free": {
        "energy_cap": 100,
        "energy_regen_rate": 1.0,
        "ad_supported": True,
        "soul_access": "standard",
        "chat_priority": "normal",
        "context_multiplier": 1.0,
        "ai_model": "gemini-flash",
        "display_name": "Free Link",
        "description": "Standard Link City access with ad-supported stability boosts"
    },
    "soul_seeker": {
        "energy_cap": 150,
        "energy_regen_rate": 2.0,
        "ad_supported": False,
        "soul_access": "standard",
        "chat_priority": "high",
        "context_multiplier": 2.0,
        "ai_model": "gemini-flash",
        "display_name": "Soul Seeker",
        "description": "Enhanced stability and ad-free experience"
    },
    "soul_master": {
        "energy_cap": 999,
        "energy_regen_rate": 999.0,
        "ad_supported": False,
        "soul_access": "premium",
        "chat_priority": "highest",
        "context_multiplier": 4.0,
        "ai_model": "gemini-pro",
        "display_name": "Soul Master",
        "description": "Unlimited stability with premium AI model access"
    },
    "architect": {
        "energy_cap": 999,
        "energy_regen_rate": 999.0,
        "ad_supported": False,
        "soul_access": "all",
        "chat_priority": "god_mode",
        "context_multiplier": 999.0,
        "ai_model": "gemini-pro",
        "display_name": "Architect",
        "description": "Developer god-mode with full system access"
    }
}

def get_tier_benefits(tier: str) -> Dict[str, Any]:
    """
    Get the benefit configuration for a specific tier.
    
    Args:
        tier: The account tier (free, soul_seeker, soul_master, architect)
        
    Returns:
        Dictionary of tier benefits
    """
    return TIER_BENEFITS.get(tier, TIER_BENEFITS["free"])

def get_energy_cap(user: User) -> int:
    """Get the maximum energy cap for a user based on their tier."""
    benefits = get_tier_benefits(user.account_tier)
    return benefits["energy_cap"]

def get_energy_regen_rate(user: User) -> float:
    """Get the energy regeneration rate multiplier for a user."""
    benefits = get_tier_benefits(user.account_tier)
    return benefits["energy_regen_rate"]

def should_show_ads(user: User) -> bool:
    """Check if ads should be shown to this user."""
    benefits = get_tier_benefits(user.account_tier)
    return benefits["ad_supported"]

def get_ai_model(user: User) -> str:
    """Get the AI model to use for this user's tier."""
    benefits = get_tier_benefits(user.account_tier)
    return benefits["ai_model"]

def get_context_multiplier(user: User) -> float:
    """Get the context window multiplier for this user's tier."""
    benefits = get_tier_benefits(user.account_tier)
    return benefits["context_multiplier"]

def can_access_soul(user: User, soul_id: str) -> bool:
    """
    Check if a user can access a specific soul based on their tier.
    
    Args:
        user: The user to check
        soul_id: The soul ID to check access for
        
    Returns:
        True if user can access this soul
    """
    benefits = get_tier_benefits(user.account_tier)
    soul_access = benefits["soul_access"]
    
    # Architect can access everything
    if soul_access == "all":
        return True
    
    # Premium souls (future expansion)
    PREMIUM_SOULS = []  # Add premium soul IDs here in v1.5.5+
    
    if soul_id in PREMIUM_SOULS:
        return soul_access == "premium"
    
    # Standard souls accessible to all
    return True

def get_tier_display_info(tier: str) -> Dict[str, str]:
    """
    Get display information for a tier (for UI).
    
    Returns:
        Dictionary with display_name and description
    """
    benefits = get_tier_benefits(tier)
    return {
        "display_name": benefits["display_name"],
        "description": benefits["description"]
    }

def get_all_tiers() -> Dict[str, Dict[str, Any]]:
    """Get all tier configurations (for subscription screen)."""
    return TIER_BENEFITS
