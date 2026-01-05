import os
import json

# Locate bots folder relative to this file
BOT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "assets", "bots")

def load_roster():
    roster = []

    # Prefer All-Bots.json if it exists
    all_path = os.path.join(BOT_FOLDER, "All-Bots.json")
    if os.path.exists(all_path):
        with open(all_path, "r", encoding="utf-8") as f:
            roster = json.load(f)
    else:
        # Fallback: load individual Bot-[Name].json files
        for filename in os.listdir(BOT_FOLDER):
            if filename.startswith("Bot-") and filename.endswith(".json"):
                path = os.path.join(BOT_FOLDER, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        bot = json.load(f)
                        roster.append(bot)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

    return roster
