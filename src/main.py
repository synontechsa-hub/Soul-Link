# main.py (Backend logic for SoulLink)
import logging
from typing import Dict, List, Any

from roster_loader import load_roster
from chat_engine import start_chat
from onboarding import start_onboarding
from progression import check_unlocks

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_card_preview(bot: Dict[str, Any]) -> Any:
    """Return the appropriate card based on affection score."""
    cards = bot.get("cards", [])
    affection = bot.get("affection", 0)

    if not cards:
        return None

    # Unlock new card every 20 affection points
    index = min(affection // 20, len(cards) - 1)
    return cards[index]

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

        if choice.lower() == 'q':
            logging.info(f"Session ended for {user_state['profile']['name']}")
            break

        try:
            choice_index = int(choice) - 1
            if choice_index < 0 or choice_index >= len(roster):
                raise ValueError

            selected_bot = roster[choice_index]
            if not selected_bot.get("unlocked", True):
                logging.info(f"{selected_bot['name']} is locked. Progress further to unlock.")
                continue

            # Start chat (backend handles logic, frontend renders)
            start_chat(selected_bot, user_state)

            # Progression check
            new_unlocks = check_unlocks(user_state, roster)
            if new_unlocks:
                logging.info(f"New companions unlocked: {', '.join(new_unlocks)}")

        except ValueError:
            logging.warning("Invalid choice entered.")

if __name__ == "__main__":
    main()