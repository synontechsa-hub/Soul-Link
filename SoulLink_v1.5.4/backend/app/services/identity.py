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