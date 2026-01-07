import json
import os
import logging
from typing import Dict, List, Optional

BOT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "assets", "bots")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def normalize_bot(bot: Dict) -> Dict:
    """Convert JSON structure into the format the app expects."""
    core = bot.get("Core Identity", {})
    personality = bot.get("Personality", {})
    voice = bot.get("Voice & Tone", {})

    return {
        "name": core.get("Name", "Unknown"),
        "archetype": core.get("Archetype", ""),
        "personality": {
            "traits": personality.get("Traits", "").split(", ") if personality.get("Traits") else [],
            "flaws": personality.get("Flaws", "").split(", ") if personality.get("Flaws") else []
        },
        "voice": {
            "quotes": voice.get("Quotes", []),
            "style": voice.get("Style", "")
        },
        # Standardized fields
        "affection": int(bot.get("Affection", 0)),
        "cards": bot.get("Cards", []),
        "responses": bot.get("Responses", {}),
        "unlocked": bot.get("unlocked", True),
        # Keep original full data if needed
        "raw": bot
    }

def load_character(name: str) -> Optional[Dict]:
    """
    Load a single character JSON file by bot name (e.g., 'Adrian').
    Returns the normalized character dict or None if not found/invalid.
    """
    filename = f"Bot-{name}.json"
    path = os.path.join(BOT_FOLDER, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return normalize_bot(data)
    except FileNotFoundError:
        logging.error(f"Character file {filename} not found in {BOT_FOLDER}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Error decoding {filename}. Check JSON formatting.")
        return None

def load_all_characters() -> List[Dict]:
    """
    Load all character JSON files in the bots folder.
    Returns a list of normalized character dicts.
    """
    characters: List[Dict] = []
    if not os.path.exists(BOT_FOLDER):
        logging.error(f"Folder {BOT_FOLDER} does not exist.")
        return characters

    for file in os.listdir(BOT_FOLDER):
        if file.startswith("Bot-") and file.endswith(".json"):
            path = os.path.join(BOT_FOLDER, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    characters.append(normalize_bot(data))
            except Exception as e:
                logging.warning(f"Skipping {file}: {e}")

    logging.info(f"Loaded {len(characters)} characters from {BOT_FOLDER}")
    return characters

def load_characters(names: List[str]) -> List[Dict]:
    """
    Load a batch of characters by name list.
    Returns only successfully loaded bots.
    """
    return [c for n in names if (c := load_character(n))]