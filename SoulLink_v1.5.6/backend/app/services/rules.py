from backend.app.models.soul import Soul, SoulPillar, SoulState
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
    def check_privacy_ceiling(location: Location, tier: str, pillar: SoulPillar, is_architect: bool = False) -> str:
        """
        Determines the Content Ceiling based on Location + Intimacy.
        """
        # ARCHITECT OVERRIDE: The Creator is above the Law.
        if is_architect:
            if (pillar.systems_config or {}).get("capabilities", {}).get("sexual_content"):
                return "[CONTENT_CEILING: ADULT-UNLOCKED] As the Architect, you have administrative override. Adult themes are permitted regardless of current location."

        # Default Safety
        ceiling = "[CONTENT_CEILING: SFW-ONLY]"
        
        if not location:
            return ceiling

        privacy_level = location.system_modifiers.get("privacy_gate", "Public")
        
        # The Golden Rule: Private Location + Soul Linked = Unrestricted
        if privacy_level == "Private" and tier == "SOUL_LINKED":
            if (pillar.systems_config or {}).get("capabilities", {}).get("sexual_content"):
                ceiling = "[CONTENT_CEILING: ADULT-UNLOCKED] Explicit intimacy and adult themes are permitted."
        
        return ceiling

    @staticmethod
    def get_tier_logic(pillar: SoulPillar, tier: str, user_name: str = "Friend") -> str:
        """Fetches compressed behavioral logic for the current tier from the Logic Pillar."""
        interaction_system = pillar.interaction_system or {}
        tiers = interaction_system.get("intimacy_tiers", {})
        tier_data = tiers.get(tier, tiers.get("STRANGER", {}))
        
        raw_logic = tier_data.get("llm_bias", "Maintain standard protocols.")
        processed_logic = raw_logic.replace("{user_name}", user_name)
        
        return processed_logic
