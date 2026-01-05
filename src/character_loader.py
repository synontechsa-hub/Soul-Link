import json
import os

BOT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "assets", "bots")

def normalize_bot(bot: dict) -> dict:
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
        # New standardized fields
        "affection": bot.get("Affection", 0),
        "cards": bot.get("Cards", []),
        "responses": bot.get("Responses", {}),
        # Keep original full data if needed
        "raw": bot
    }

def load_character(name: str) -> dict | None:
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
        print(f"❌ Character file {filename} not found in {BOT_FOLDER}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error decoding {filename}. Check JSON formatting.")
        return None

def load_all_characters() -> list[dict]:
    """
    Load all character JSON files in the bots folder.
    Returns a list of normalized character dicts.
    """
    characters = []
    if not os.path.exists(BOT_FOLDER):
        print(f"❌ Folder {BOT_FOLDER} does not exist.")
        return characters

    for file in os.listdir(BOT_FOLDER):
        if file.startswith("Bot-") and file.endswith(".json"):
            path = os.path.join(BOT_FOLDER, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    characters.append(normalize_bot(data))
            except Exception as e:
                print(f"⚠️ Skipping {file}: {e}")
    return characters