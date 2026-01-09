import logging
import json
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ─────────────────────────────────────────────
# 📁 STATE STORAGE
# ─────────────────────────────────────────────

# Path to store onboarding state
STATE_FILE = Path(__file__).parent / "assets" / "user_profile.json"


def start_onboarding(name: str = "", age_input: str = "", gender_input: str = "") -> Dict[str, Any]:
    """
    Build user profile and initial state for SoulLink.
    Parameters are passed in by the frontend (instead of console input).
    Returns:
    {
        "profile": { "name": str, "age": int|None, "gender": str },
        "milestones": [str],
        "affection": { bot_name: int },
        "onboarding_complete": bool
    }
    """

    # ─────────────────────────────────────────────
    # 🎂 AGE NORMALIZATION
    # ─────────────────────────────────────────────

    # Convert age to int if possible
    age = None
    if age_input:
        try:
            age = int(age_input)
        except (ValueError, TypeError):
            logging.warning(f"Invalid age input '{age_input}', defaulting to None")

    # ─────────────────────────────────────────────
    # 🧬 GENDER NORMALIZATION
    # ─────────────────────────────────────────────

    # Normalize gender input
    gender_map = {
        "male": "Male",
        "m": "Male",
        "man": "Male",
        "female": "Female",
        "f": "Female",
        "woman": "Female",
        "other": "Other",
        "o": "Other",
        "unspecified": "Unspecified",
        "u": "Unspecified"
    }
    gender = "Unspecified"
    if gender_input:
        gender = gender_map.get(gender_input.strip().lower(), gender_input.capitalize())

    # ─────────────────────────────────────────────
    # 🧍 USER PROFILE
    # ─────────────────────────────────────────────

    # Build user profile
    user_profile = {
        "name": name if name else "Traveler",
        "age": age,
        "gender": gender
    }

    logging.info(
        f"Profile created for {user_profile['name']} "
        f"(Age={user_profile['age']}, Gender={user_profile['gender']})"
    )

    # ─────────────────────────────────────────────
    # 🧠 FULL STATE OBJECT
    # ─────────────────────────────────────────────

    # Build full state
    state = {
        "profile": user_profile,
        "milestones": ["onboarding_started", "onboarding_completed"],
        "affection": {},
        "onboarding_complete": True
    }

    # ─────────────────────────────────────────────
    # 💾 PERSIST STATE TO DISK
    # ─────────────────────────────────────────────

    # Persist to disk
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with STATE_FILE.open("w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        logging.info(f"Onboarding state saved to {STATE_FILE}")
    except Exception as e:
        logging.error(f"Failed to save onboarding state: {e}")

    return state
