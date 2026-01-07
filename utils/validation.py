# utils/validation.py
import logging
from typing import Dict

def validate_bot(bot: Dict) -> None:
    """
    Validate normalized bot structure.
    Logs warnings for missing or suspicious data.
    Does NOT raise exceptions.
    """

    name = bot.get("name", "Unknown")

    traits = bot.get("personality", {}).get("traits", [])
    flaws = bot.get("personality", {}).get("flaws", [])
    quotes = bot.get("voice", {}).get("quotes", [])

    if not traits:
        logging.warning(f"[{name}] has no personality traits defined.")

    if not flaws:
        logging.warning(f"[{name}] has no flaws defined.")

    if not quotes:
        logging.warning(f"[{name}] has no voice quotes defined.")

    affection = bot.get("affection", 0)
    if affection < 0:
        logging.warning(f"[{name}] has negative affection ({affection}).")

    cards = bot.get("cards", [])
    if cards and not isinstance(cards, list):
        logging.warning(f"[{name}] cards field is not a list.")

    if "archetype" not in bot or not bot["archetype"]:
        logging.warning(f"[{name}] has no archetype defined.")
