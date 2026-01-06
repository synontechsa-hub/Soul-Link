import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def start_onboarding(name: str = "", age_input: str = "", gender_input: str = "") -> Dict[str, Any]:
    """
    Build user profile and initial state for SoulLink.
    Parameters are passed in by the frontend (instead of console input).
    Returns:
    {
        "profile": { "name": str, "age": int|None, "gender": str },
        "milestones": [str],
        "affection": { bot_name: int }
    }
    """
    # Convert age to int if possible
    try:
        age = int(age_input) if age_input else None
    except ValueError:
        age = None

    # Normalize gender
    valid_genders = {"male": "Male", "female": "Female", "other": "Other"}
    gender = valid_genders.get(gender_input.lower(), gender_input.capitalize() if gender_input else "Unspecified")

    # Build user profile
    user_profile = {
        "name": name if name else "Traveler",
        "age": age,
        "gender": gender
    }

    logging.info(f"Profile created for {user_profile['name']}")

    # Return user state with profile + milestones + affection tracking
    return {
        "profile": user_profile,
        "milestones": ["onboarding_started"],
        "affection": {}
    }