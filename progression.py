import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Raise threshold for better pacing
AFFECTION_THRESHOLD = 20

def check_unlocks(user_state: Dict, roster: List[Dict]) -> List[str]:
    """
    Unlock new bots or features based on user progression.
    - Bots unlock when affection reaches a threshold.
    - Bots unlock when specific milestones are achieved.
    Returns a list of newly unlocked bot names.
    """
    unlocked: List[str] = []
    milestones = user_state.get("milestones", [])

    for bot in roster:
        if not bot.get("unlocked", True):
            affection_met = bot.get("affection", 0) >= bot.get("unlock_affection", AFFECTION_THRESHOLD)
            milestone_met = f"Chatted with {bot['name']}" in milestones

            if affection_met or milestone_met:
                bot["unlocked"] = True
                unlocked.append(bot["name"])
                reason = "affection" if affection_met else "milestones"
                logging.info(f"{bot['name']} unlocked through {reason}")

    return unlocked