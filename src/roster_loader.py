# roster_loader.py
from character_loader import load_all_characters

def load_roster(folder: str = "assets/json") -> list[dict]:
    """
    Load the full SoulLink roster from JSON character files.
    Returns a list of validated character dicts.
    """
    roster = load_all_characters(folder)

    if not roster:
        print("⚠️ No valid companions found in roster.")
    else:
        print(f"✅ Loaded {len(roster)} companions from {folder}")

    return roster