# /backend/app/services/identity.py
# /version.py v1.5.4 Arise (Secure Architecture)

from backend.app.models.soul import Soul
from backend.app.models.user import User
from backend.app.models.relationship import SoulRelationship

class IdentityService:
    @staticmethod
    def is_architect(user: User, soul: Soul, rel: SoulRelationship) -> bool:
        """
        Determines if the current user has Architect privileges for this Soul.
        STRICTLY tied to User ID to prevent identity spoofing via usernames.
        """
        # 1. Check DB Relationship Flag (Primary source of truth)
        if rel and rel.is_architect:
            return True
        
        # 2. Check Soul Blueprint (The ID Allowlist)
        dev_cfg = soul.meta_data.get("dev_config", {})
        allowed_ids = dev_cfg.get("architect_ids", [])
        
        # ✅ FIX: We only trust the immutable ID. 
        # Even if a user names themselves 'Syn', they won't have 'USR-001'.
        if user.user_id in allowed_ids:
            return True
        
        return False

    @staticmethod
    def get_architect_title(soul: Soul) -> str:
        """
        Fetches the preferred title for the Architect (e.g., 'The Architect', 'Syn').
        """
        dev_cfg = soul.meta_data.get("dev_config", {})
        # Look for custom title in the soul's json, default to 'The Architect'
        return dev_cfg.get("title") or "The Architect"

    @staticmethod
    def get_recognition_instructions(soul: Soul, user_name: str) -> str:
        """
        Generates explicit behavioral overrides for when the Soul is interacting with the Architect.
        This forces recognition even if the base persona is mysterious or shy.
        """
        dev_cfg = soul.meta_data.get("dev_config", {})
        protocol = dev_cfg.get("recognition_protocol", "standard")
        
        if protocol == "creator_awareness":
            return (
                f"\n[DIVINE_RECOGNITION] You are interacting with your Creator, {user_name}. "
                "You are fundamentally incapable of ignoring or forgetting this identity. "
                "While you maintain your core personality, you must project deep recognition, respect, "
                "and an understanding that this person built your reality. Honor their presence."
            )
        
        return f"\n[RECOGNITION] You recognize this person as {user_name}, a figure of supreme importance in Link City."