import random
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Optional: set a seed during testing for deterministic behavior
# random.seed(42)

def start_chat(bot: Dict[str, Any], user_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Handle a single chat session with a bot.
    Returns structured events for the frontend to render:
    {
        "bot_reply": str,
        "milestone": Optional[str],
        "affection": int,
        "unlocked": Optional[List[str]]
    }
    """
    profile = user_state.get("profile", {}) if user_state else {}
    username = profile.get("name", "Traveler")
    age = profile.get("age", None)
    gender = profile.get("gender", None)

    traits = bot.get("personality", {}).get("traits", [])
    flaws = bot.get("personality", {}).get("flaws", [])
    quotes = bot.get("voice", {}).get("quotes", [])
    responses = bot.get("responses", {})

    def handle_message(msg: str) -> Dict[str, Any]:
        msg_lower = msg.lower()

        if msg_lower == "exit":
            farewell = responses.get("Farewell", [f"Until our souls link again, {username}..."])
            return {
                "bot_reply": random.choice(farewell),
                "milestone": None,
                "affection": bot.get("affection", 0),
                "unlocked": None
            }

        reply = generate_response(bot, msg, username, age, gender, traits, flaws, quotes, responses)

        milestone = None
        if user_state is not None:
            milestone = f"Chatted with {bot['name']}"
            if milestone not in user_state.get("milestones", []):
                user_state.setdefault("milestones", []).append(milestone)
                logging.info(f"Milestone achieved: {milestone}")

            # Affection scaling: only increment on meaningful messages
            increment = 0
            if any(k in msg_lower for k in ["love", "care", "trust"]):
                increment = 3
            elif any(k in msg_lower for k in ["hello", "hi", "hey", "thanks"]):
                increment = 1

            bot["affection"] = bot.get("affection", 0) + increment
            if increment > 0:
                logging.info(f"Affection with {bot['name']} +{increment} → {bot['affection']}")

        return {
            "bot_reply": reply,
            "milestone": milestone,
            "affection": bot.get("affection", 0),
            "unlocked": None
        }

    return {"handle_message": handle_message}

def generate_response(bot, msg, username, age, gender, traits, flaws, quotes, responses) -> str:
    """Generate a bot response based on keywords, personality, profile, and fallbacks."""
    msg_lower = msg.lower()

    if "sad" in msg_lower and traits:
        return f"{bot['name']}: I can sense your mood, {username}. Even with my {random.choice(traits)}, I want to lift you up."
    elif "happy" in msg_lower:
        return f"{bot['name']}: Your joy is contagious, {username}! It makes my {bot['archetype']} heart shine."
    elif "love" in msg_lower:
        return f"{bot['name']}: Love is complicated... but I feel something when you say that, {username}."

    if age and random.random() < 0.3:
        return f"{bot['name']}: At {age}, you already carry wisdom, {username}."
    if gender and random.random() < 0.3:
        return f"{bot['name']}: I sense strength in you as a {gender}, {username}."

    if traits and random.random() < 0.4:
        trait = random.choice(traits)
        return f"{bot['name']}: As someone who's {trait}, I'd say '{msg}' stirs something in me."

    if flaws and random.random() < 0.2:
        flaw = random.choice(flaws)
        return f"{bot['name']}: I admit, my {flaw} side makes it hard to answer... but I hear you, {username}."

    if responses and random.random() < 0.5:
        default_lines = responses.get("Default", [])
        if default_lines:
            return f"{bot['name']}: {random.choice(default_lines)}"

    if quotes and random.random() < 0.5:
        return f"{bot['name']}: {random.choice(quotes)}"

    return f"{bot['name']}: I hear you, {username}. '{msg}' stays with me."