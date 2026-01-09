import json
import os
import logging
from typing import Dict, List, Optional
from utils.validation import validate_bot

# ─────────────────────────────────────────────
# 🧭 PATH RESOLUTION
# ─────────────────────────────────────────────
# Align path with roster_loader.py (project root/assets/bots)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BOT_FOLDER = os.path.join(PROJECT_ROOT, "assets", "bots")

# ─────────────────────────────────────────────
# 🪵 LOGGING
# ─────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ─────────────────────────────────────────────
# 🧠 NORMALIZATION HELPERS
# ─────────────────────────────────────────────

def normalize_list(value) -> List[str]:
    """Normalize a value into a list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return []

# ─────────────────────────────────────────────
# 🧠 BOT NORMALIZATION
# ─────────────────────────────────────────────

def normalize_bot(bot: Dict) -> Dict:
    """Convert JSON structure into the format the app expects."""
    core = bot.get("Core Identity", {})
    personality = bot.get("Personality", {})
    voice = bot.get("Voice & Tone", {})

    normalized = {
        "name": core.get("Name", "Unknown"),
        "archetype": core.get("Archetype", ""),
        "personality": {
            "traits": normalize_list(personality.get("Traits")),
            "flaws": normalize_list(personality.get("Flaws"))
        },
        "voice": {
            "quotes": normalize_list(voice.get("Quotes")),
            "style": voice.get("Style", "")
        },
        "affection": int(bot.get("Affection", 0)),
        "cards": bot.get("Cards", []),
        "responses": bot.get("Responses", {}),
        "unlocked": bot.get("unlocked", True),
        "raw": bot
    }

    validate_bot(normalized)
    return normalized

# ─────────────────────────────────────────────
# 📄 SINGLE CHARACTER LOADING
# ─────────────────────────────────────────────

def load_character(name: str) -> Optional[Dict]:
    """Load a single character JSON file by bot name (e.g., 'Adrian')."""
    """Load a single character JSON file by bot name (e.g., 'Adrian')."""
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

# ─────────────────────────────────────────────
# 📦 BULK CHARACTER LOADING
# ─────────────────────────────────────────────

def load_all_characters() -> List[Dict]:
    """Load all character JSON files in the bots folder, avoiding duplicates."""
    """Load all character JSON files in the bots folder, avoiding duplicates."""
    characters: List[Dict] = []
    seen_names = set()

    if not os.path.exists(BOT_FOLDER):
        logging.error(f"Folder {BOT_FOLDER} does not exist.")
        return characters

    for file in os.listdir(BOT_FOLDER):
        if file.startswith("Bot-") and file.endswith(".json"):
            path = os.path.join(BOT_FOLDER, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    normalized = normalize_bot(data)
                    if normalized["name"] not in seen_names:
                        characters.append(normalized)
                        seen_names.add(normalized["name"])
            except Exception as e:
                logging.warning(f"Skipping {file}: {e}")

    logging.info(f"Loaded {len(characters)} characters from {BOT_FOLDER}")
    return characters

# ─────────────────────────────────────────────
# 📦 SELECTIVE CHARACTER LOADING
# ─────────────────────────────────────────────

def load_characters(names: List[str]) -> List[Dict]:
    """Load a batch of characters by name list."""
    characters: List[Dict] = []
    seen_names = set()

    for n in names:
        c = load_character(n)
        if c and c["name"] not in seen_names:
            characters.append(c)
            seen_names.add(c["name"])

    return characters
