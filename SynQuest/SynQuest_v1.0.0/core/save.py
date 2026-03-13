import json
import os
from .state import GameState

SAVE_DIR = "data/saves"

def save_game(state: GameState, filename: str = "save_001.json"):
    os.makedirs(SAVE_DIR, exist_ok=True)
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, "w") as f:
        f.write(state.model_dump_json(indent=4))

def load_game(filename: str = "save_001.json") -> GameState:
    filepath = os.path.join(SAVE_DIR, filename)
    if not os.path.exists(filepath):
        return GameState() # Return fresh state if no save exists
    
    with open(filepath, "r") as f:
        data = json.load(f)
        return GameState(**data)
