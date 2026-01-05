import json
import os

def load_character(name, folder="assets/json"):
    filename = f"{name}.json"
    path = os.path.join(folder, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)