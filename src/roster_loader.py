import os
import json
import logging
from typing import Dict, List

BOT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "assets", "bots")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def normalize_bot(bot: Dict) -> Dict:
    """Convert JSON structure into the format main.py and chat_engine expect."""
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

def load_roster() -> List[Dict]:
    """
    Load all bots from All-Bots.json or individual Bot-*.json files.
    Returns a list of normalized bot dicts.
    """
    roster: List[Dict] = []
    all_path = os.path.join(BOT_FOLDER, "All-Bots.json")

    if os.path.exists(all_path):
        try:
            with open(all_path, "r", encoding="utf-8") as f:
                bots = json.load(f)
                roster = [normalize_bot(b) for b in bots]
        except Exception as e:
            logging.error(f"Error loading All-Bots.json: {e}")
    else:
        for filename in os.listdir(BOT_FOLDER):
            if filename.startswith("Bot-") and filename.endswith(".json"):
                path = os.path.join(BOT_FOLDER, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        bot = json.load(f)
                        roster.append(normalize_bot(bot))
                except Exception as e:
                    logging.warning(f"Skipping {filename}: {e}")

    logging.info(f"Loaded {len(roster)} bots from {BOT_FOLDER}")
    return roster