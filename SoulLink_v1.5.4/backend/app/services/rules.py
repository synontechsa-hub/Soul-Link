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
        """Standardizes the Intimacy Ladder."""
        if score >= 86: return "SOUL_LINKED"
        if score >= 71: return "FRIENDSHIP"
        if score >= 41: return "TRUSTED"
        if score >= 21: return "ACQUAINTANCE"
        return "STRANGER"

    @staticmethod
    def check_privacy_ceiling(location: Location, tier: str, soul: Soul, is_architect: bool = False) -> str:
        """
        Determines the Content Ceiling based on Location + Intimacy.
        Returns the system instruction tag to inject into the LLM.
        """
        # 🗝️ ARCHITECT OVERRIDE: The Creator is above the Law.
        if is_architect:
            if soul.meta_data.get("capabilities", {}).get("sexual_content"):
                return "[CONTENT_CEILING: ADULT-UNLOCKED] As the Architect, you have administrative override. Adult themes are permitted regardless of current location."

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
    def get_tier_logic(soul: Soul, tier: str, user_name: str = "Friend") -> str:
        """Fetches compressed behavioral logic for the current tier."""
        # 🧪 v1.5.4 Arise uses 'intimacy_tiers' key
        tiers = soul.interaction_engine.get("intimacy_tiers", {})
        tier_data = tiers.get(tier, tiers.get("STRANGER", {}))
        
        # ✂️ Semantic Compression
        raw_logic = tier_data.get("logic", "Maintain standard protocols.")
        
        # 👤 Personalization
        processed_logic = raw_logic.replace("{user_name}", user_name)
        
        return processed_logic