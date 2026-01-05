# character_loader.py
import json
import os

def load_character(name: str, folder: str = "assets/json") -> dict | None:
    """
    Load a single character JSON file by name.
    Returns the character dict or None if not found/invalid.
    """
    filename = f"{name}.json"
    path = os.path.join(folder, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if validate_character(data):
                return data
            else:
                print(f"⚠️ Invalid character data in {filename}")
                return None
    except FileNotFoundError:
        print(f"❌ Character file {filename} not found in {folder}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error decoding {filename}. Check JSON formatting.")
        return None


def load_all_characters(folder: str = "assets/json") -> list[dict]:
    """
    Load all character JSON files in the given folder.
    Returns a list of valid character dicts.
    """
    characters = []
    if not os.path.exists(folder):
        print(f"❌ Folder {folder} does not exist.")
        return characters

    for file in os.listdir(folder):
        if file.endswith(".json"):
            path = os.path.join(folder, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if validate_character(data):
                        characters.append(data)
                    else:
                        print(f"⚠️ Skipping invalid character file {file}")
            except Exception as e:
                print(f"⚠️ Skipping {file}: {e}")
    return characters


def validate_character(data: dict) -> bool:
    """
    Ensure the character JSON has required fields.
    """
    required = ["name", "archetype", "personality", "voice"]
    for field in required:
        if field not in data:
            print(f"⚠️ Missing field '{field}' in character {data.get('name', 'Unknown')}")
            return False
    return True