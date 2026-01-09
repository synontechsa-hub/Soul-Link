import json
import os
from datetime import datetime

# ─────────────────────────────────────────────
# 🗂️ USER DATA CONFIGURATION
# ─────────────────────────────────────────────

BASE_DIR = "data/users"
DEFAULT_USER_ID = "local_user"

# ─────────────────────────────────────────────
# 📁 USER DIRECTORY MANAGEMENT
# ─────────────────────────────────────────────

def user_dir(user_id: str = DEFAULT_USER_ID) -> str:
    """
    Ensure and return the base directory for a given user.
    Creates:
    - data/users/<user_id>/
    - data/users/<user_id>/bots/
    """
    path = os.path.join(BASE_DIR, user_id)

    # Ensure base user directory exists
    os.makedirs(path, exist_ok=True)

    # Ensure bot memory directory exists
    os.makedirs(os.path.join(path, "bots"), exist_ok=True)

    return path

# ─────────────────────────────────────────────
# 👤 USER PROFILE LOADING
# ─────────────────────────────────────────────

def load_user(user_id: str = DEFAULT_USER_ID) -> dict:
    """
    Load an existing user profile.
    If none exists, create a default profile and persist it.
    """
    path = os.path.join(user_dir(user_id), "profile.json")

    if not os.path.exists(path):
        profile = {
            "user_id": user_id,
            "display_name": "Guest",
            "created_at": datetime.utcnow().isoformat(),
            "last_active_bot": None,
            "settings": {
                "memory_enabled": True
            },
        }

        save_user(profile)
        return profile

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ─────────────────────────────────────────────
# 💾 USER PROFILE PERSISTENCE
# ─────────────────────────────────────────────

def save_user(profile: dict):
    """
    Persist a user profile to disk.
    """
    path = os.path.join(user_dir(profile["user_id"]), "profile.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
