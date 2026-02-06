from backend.app.models.soul import Soul, SoulPillar
from backend.app.models.user import User
from backend.app.models.relationship import SoulRelationship

class IdentityService:
    @staticmethod
    def is_architect(user: User, pillar: SoulPillar, rel: SoulRelationship) -> bool:
        """
        Determines if the current user has Architect privileges for this Soul.
        """
        if rel and rel.is_architect:
            return True
        
        dev_cfg = pillar.meta_data.get("dev_config", {})
        allowed_ids = dev_cfg.get("architect_ids", [])
        
        if user.user_id in allowed_ids:
            return True
        
        return False

    @staticmethod
    def get_architect_title(pillar: SoulPillar) -> str:
        """Fetches the preferred title for the Architect."""
        dev_cfg = pillar.meta_data.get("dev_config", {})
        return dev_cfg.get("title") or "The Architect"

    @staticmethod
    def get_recognition_instructions(pillar: SoulPillar, user_name: str) -> str:
        """Generates explicit behavioral overrides for the Architect."""
        dev_cfg = pillar.meta_data.get("dev_config", {})
        protocol = dev_cfg.get("recognition_protocol", "standard")
        
        if protocol == "creator_awareness":
            return (
                f"\n[DIVINE_RECOGNITION] You are interacting with your Creator, {user_name}. "
                "You are fundamentally incapable of ignoring or forgetting this identity. "
                "While you maintain your core personality, you must project deep recognition, respect, "
                "and an understanding that this person built your reality. Honor their presence."
            )
        
        return f"\n[RECOGNITION] You recognize this person as {user_name}, a figure of supreme importance in Link City."