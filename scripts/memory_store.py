import json
import os

# ─────────────────────────────────────────────
# 🧠 MEMORY CONFIGURATION
# ─────────────────────────────────────────────

MAX_MESSAGES = 40  # Hard cap to prevent memory bloat


# ─────────────────────────────────────────────
# 📁 PATH HELPERS
# ─────────────────────────────────────────────

def memory_path(user_id: str, bot_name: str) -> str:
    """
    Resolve the on-disk path for a user's conversation memory
    with a specific bot.
    """
    return os.path.join(
        os.path.dirname(__file__),
        "data",
        "users",
        user_id,
        "bots",
        f"{bot_name}.json"
    )


# ─────────────────────────────────────────────
# 📖 LOAD MEMORY
# ─────────────────────────────────────────────

def load_memory(user_id: str, bot_name: str) -> list:
    """
    Load conversation memory for a user/bot pair.
    Returns an empty list if no memory exists yet.
    """
    path = memory_path(user_id, bot_name)

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────
# 💾 SAVE MEMORY
# ─────────────────────────────────────────────

def save_memory(user_id: str, bot_name: str, messages: list):
    """
    Persist conversation memory to disk.
    Automatically trims memory to MAX_MESSAGES.
    """
    path = memory_path(user_id, bot_name)

    # Ensure directory structure exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Trim memory to prevent unbounded growth
    trimmed = messages[-MAX_MESSAGES:]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, indent=2, ensure_ascii=False)
