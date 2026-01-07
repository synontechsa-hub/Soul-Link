import json
import os

MAX_MESSAGES = 40


def memory_path(user_id: str, bot_name: str) -> str:
    return os.path.join(
        "data/users", user_id, "bots", f"{bot_name}.json"
    )


def load_memory(user_id: str, bot_name: str) -> list:
    path = memory_path(user_id, bot_name)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(user_id: str, bot_name: str, messages: list):
    os.makedirs(os.path.dirname(memory_path(user_id, bot_name)), exist_ok=True)
    trimmed = messages[-MAX_MESSAGES:]
    with open(memory_path(user_id, bot_name), "w", encoding="utf-8") as f:
        json.dump(trimmed, f, indent=2, ensure_ascii=False)
