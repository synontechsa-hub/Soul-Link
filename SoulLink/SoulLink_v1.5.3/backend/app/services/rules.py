# /backend/app/services/rules.py
# /version.py
# /_dev/

# "Rules are made to be broken... but not these ones."
# - Hey are you the Trailblazer? All aboard the Astral Express!

from backend.app.models.soul import Soul
from backend.app.models.location import Location

class Gatekeeper:
    @staticmethod
    def get_current_tier(score: int) -> str:
        """Standardizes the Intimacy Ladder across the entire app."""
        if score >= 86: return "SOUL_LINKED"
        if score >= 71: return "FRIENDSHIP"
        if score >= 41: return "TRUSTED"
        if score >= 21: return "ACQUAINTANCE"
        return "STRANGER"

    @staticmethod
    def check_privacy_ceiling(location: Location, tier: str, soul: Soul) -> str:
        """
        Determines the Content Ceiling based on Location + Intimacy.
        Returns the system instruction tag to inject into the LLM.
        """
        # Default Safety
        ceiling = "[CONTENT_CEILING: SFW-ONLY]"
        
        if not location:
            return ceiling

        privacy_level = location.system_modifiers.get("privacy_gate", "Public")
        
        # The Golden Rule: Private Location + Soul Linked = Unrestricted
        if privacy_level == "Private" and tier == "SOUL_LINKED":
            if soul.meta_data.get("capabilities", {}).get("sexual_content"):
                ceiling = "[CONTENT_CEILING: ADULT-UNLOCKED] Explicit intimacy and adult themes are permitted."
        
        return ceiling

    @staticmethod
    def get_tier_logic(soul: Soul, tier: str) -> str:
        """Fetches the specific behavioral instructions for the current tier."""
        tiers = soul.interaction_engine.get("tiers", {})
        # Fallback to STRANGER if the tier is missing
        tier_data = tiers.get(tier, tiers.get("STRANGER", {}))
        return tier_data.get("logic", "Maintain standard protocols.")