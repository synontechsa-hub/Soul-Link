import json
import os
from datetime import datetime

BASE_DIR = "data/users"
DEFAULT_USER_ID = "local_user"


def user_dir(user_id: str = DEFAULT_USER_ID) -> str:
    path = os.path.join(BASE_DIR, user_id)
    os.makedirs(path, exist_ok=True)
    os.makedirs(os.path.join(path, "bots"), exist_ok=True)
    return path


def load_user(user_id: str = DEFAULT_USER_ID) -> dict:
    path = os.path.join(user_dir(user_id), "profile.json")

    if not os.path.exists(path):
        profile = {
            "user_id": user_id,
            "display_name": "Guest",
            "created_at": datetime.utcnow().isoformat(),
            "last_active_bot": None,
            "settings": {"memory_enabled": True},
        }
        save_user(profile)
        return profile

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user(profile: dict):
    path = os.path.join(user_dir(profile["user_id"]), "profile.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
