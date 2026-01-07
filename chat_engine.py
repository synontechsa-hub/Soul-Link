# chat_engine.py
"""
Chat engine for SoulLink.
Handles per-session bot conversations, short-term memory,
affection progression, and response generation.

Phase 2 introduces:
- Conversation memory (topic, emotion, turn count)
- Deterministic behavior support (via DEBUG_DETERMINISTIC)
"""

import random
import logging
from typing import Dict, Any, Optional, Tuple

from version import DEBUG_DETERMINISTIC

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Enable deterministic behavior for testing/debugging
if DEBUG_DETERMINISTIC:
    random.seed(42)
    logging.info("Deterministic chat mode enabled (DEBUG_DETERMINISTIC)")


# -----------------------------
# Conversation helpers
# -----------------------------

def infer_topic_and_emotion(msg: str) -> Tuple[Optional[str], str]:
    """
    Lightweight NLP inference for topic and emotion.
    Keeps logic simple and predictable.
    """

    msg_lower = msg.lower()

    topics = {
        "fashion": ["fashion", "style", "dress", "clothes"],
        "art": ["art", "painting", "draw", "canvas"],
        "affection": ["love", "care", "trust", "feel"],
        "greeting": ["hello", "hi", "hey"]
    }

    emotions = {
        "sad": ["sad", "down", "lonely"],
        "happy": ["happy", "joy", "excited"],
        "affectionate": ["love", "miss", "care"],
        "neutral": []
    }

    topic = next(
        (t for t, keys in topics.items() if any(k in msg_lower for k in keys)),
        None
    )

    emotion = next(
        (e for e, keys in emotions.items() if any(k in msg_lower for k in keys)),
        "neutral"
    )

    return topic, emotion


# -----------------------------
# Chat session entry point
# -----------------------------

def start_chat(bot: Dict[str, Any], user_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Start a chat session with a specific bot.

    Returns:
    {
        "handle_message": callable
    }

    The frontend calls handle_message(msg) per user message.
    """

    profile = user_state.get("profile", {}) if user_state else {}
    username = profile.get("name", "Traveler")
    age = profile.get("age")
    gender = profile.get("gender")

    traits = bot.get("personality", {}).get("traits", [])
    flaws = bot.get("personality", {}).get("flaws", [])
    quotes = bot.get("voice", {}).get("quotes", [])
    responses = bot.get("responses", {})

    # Short-term conversation memory (per session)
    memory = {
        "last_topic": None,
        "last_emotion": None,
        "turn_count": 0
    }

    def handle_message(msg: str) -> Dict[str, Any]:
        """
        Process a single user message and return a structured response
        for the frontend to render.
        """

        msg_lower = msg.lower().strip()
        memory["turn_count"] += 1

        # Detect topic & emotion
        topic, emotion = infer_topic_and_emotion(msg)
        if topic:
            memory["last_topic"] = topic
        if emotion:
            memory["last_emotion"] = emotion

        logging.debug(
            f"[{bot['name']}] Turn {memory['turn_count']} | "
            f"Topic={memory['last_topic']} Emotion={memory['last_emotion']}"
        )

        # Exit handling
        if msg_lower == "exit":
            farewell = responses.get(
                "Farewell",
                [f"Until our souls link again, {username}..."]
            )
            return {
                "bot_reply": random.choice(farewell),
                "milestone": None,
                "affection": bot.get("affection", 0),
                "unlocked": None
            }

        # Generate reply
        reply = generate_response(
            bot=bot,
            msg=msg,
            username=username,
            age=age,
            gender=gender,
            traits=traits,
            flaws=flaws,
            quotes=quotes,
            responses=responses,
            memory=memory
        )

        # Progression & affection
        milestone = None
        if user_state is not None:
            milestone = f"Chatted with {bot['name']}"
            if milestone not in user_state.get("milestones", []):
                user_state.setdefault("milestones", []).append(milestone)
                logging.info(f"Milestone achieved: {milestone}")

            # Affection scaling (intentionally conservative)
            increment = 0
            if memory["last_emotion"] == "affectionate":
                increment = 3
            elif memory["last_topic"] == "greeting":
                increment = 1

            if increment > 0:
                bot["affection"] = bot.get("affection", 0) + increment
                logging.info(
                    f"Affection with {bot['name']} +{increment} → {bot['affection']}"
                )

        return {
            "bot_reply": reply,
            "milestone": milestone,
            "affection": bot.get("affection", 0),
            "unlocked": None
            "unlocked": None
        }

    return {"handle_message": handle_message}


# -----------------------------
# Response generation
# -----------------------------

def generate_response(
    bot: Dict[str, Any],
    msg: str,
    username: str,
    age: Optional[int],
    gender: Optional[str],
    traits: list,
    flaws: list,
    quotes: list,
    responses: Dict[str, list],
    memory: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate a bot response using:
    - Conversation memory
    - Personality traits/flaws
    - User profile
    - Fallback randomness
    """

    msg_lower = msg.lower()

    # Memory-driven responses (highest priority)
    if memory:
        if memory.get("last_topic") == "fashion":
            return f"{bot['name']}: Style is a language, {username}. What you wear whispers who you are."

        if memory.get("last_emotion") == "sad":
            return f"{bot['name']}: Even shadows can be gentle. You don’t have to carry that alone, {username}."

    # Keyword-based logic
    if "happy" in msg_lower:
        return f"{bot['name']}: Your joy is contagious, {username}. It suits you."

    if "love" in msg_lower:
        return f"{bot['name']}: Love is a delicate thing… but I feel it when you speak, {username}."

    # Profile-aware flavor
    if age and random.random() < 0.25:
        return f"{bot['name']}: At {age}, you already carry stories worth listening to, {username}."

    if gender and random.random() < 0.25:
        return f"{bot['name']}: There’s strength in how you carry yourself as a {gender}, {username}."

    # Personality-driven responses
    if traits and random.random() < 0.4:
        trait = random.choice(traits)
        return f"{bot['name']}: Being {trait}, I find your words linger longer than expected."

    if flaws and random.random() < 0.2:
        flaw = random.choice(flaws)
        return f"{bot['name']}: My {flaw} nature makes me hesitate… but I’m listening."

    # Scripted responses
    if responses and random.random() < 0.5:
        defaults = responses.get("Default", [])
        if defaults:
            return f"{bot['name']}: {random.choice(defaults)}"

    if quotes and random.random() < 0.5:
        return f"{bot['name']}: {random.choice(quotes)}"

    # Absolute fallback
    return f"{bot['name']}: I hear you, {username}. Tell me more."
