# The artist formerly known as main.py
# Purple Rain... Python Rain more like it...
# run_backend.py

import logging
from typing import Dict, List, Any

# ─────────────────────────────────────────────
# 🧩 CORE BACKEND IMPORTS
# ─────────────────────────────────────────────
# What was once broken, was magically whole again

from scripts.roster_loader import load_roster
from scripts.chat_engine import start_chat
from scripts.onboarding import start_onboarding
from scripts.progression import check_unlocks

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ─────────────────────────────────────────────
# 🃏 CARD PREVIEW LOGIC
# ─────────────────────────────────────────────
# Shuffle em and deal em

def get_card_preview(bot: Dict[str, Any]) -> Any:
    """Return the appropriate card based on affection score."""
    cards = bot.get("cards", [])
    affection = bot.get("affection", 0)

    if not cards: 
        return None # 404

    # Unlock new card every x affection points (WValue needs reviewing)
    index = min(affection // 20, len(cards) - 1)
    return cards[index]

# ─────────────────────────────────────────────
# 📋 ROSTER ENRICHMENT (FRONTEND-FACING)
# ─────────────────────────────────────────────

def explore_roster(roster: List[Dict], user_state: Dict) -> List[Dict]:
    """
    Return roster data for frontend rendering.
    Each bot dict includes status, traits, quotes, affection, and card preview.
    """
    username = user_state.get("profile", {}).get("name", "Traveler")
    logging.info(f"Preparing roster for {username}")

    enriched_roster = []

    for bot in roster:
        enriched_roster.append({
            "name": bot.get("name", "Unknown"),
            "archetype": bot.get("archetype", "Unknown"),
            "traits": bot.get("personality", {}).get("traits", []),
            "flaws": bot.get("personality", {}).get("flaws", []),
            "quotes": bot.get("voice", {}).get("quotes", []),
            "affection": bot.get("affection", 0),
            "card_preview": get_card_preview(bot),
            "unlocked": bot.get("unlocked", True),
        })

    return enriched_roster

# ─────────────────────────────────────────────
# 🚀 BACKEND ENTRY POINT
# ─────────────────────────────────────────────

def main() -> None:
    """Backend entry point for SoulLink logic."""
    logging.info("Starting SoulLink backend...")

    roster = load_roster()
    if not roster:
        logging.error("No companions available. Please check your roster files.")
        return

    user_state = start_onboarding()

    while True:
        enriched_roster = explore_roster(roster, user_state)

        # Instead of printing, return roster data to frontend
        logging.info(f"Roster prepared with {len(enriched_roster)} bots")

        choice = input("Choose a companion (number), or 'q' to quit: ")

        if choice.lower() == "q":
            logging.info(f"Session ended for {user_state['profile']['name']}")
            break

        try:
            choice_index = int(choice) - 1
            if choice_index < 0 or choice_index
