def check_unlocks(user_state, roster):
    """
    Unlock new bots or features based on user progression.
    - Bots unlock when affection reaches a threshold.
    - Bots unlock when specific milestones are achieved.
    """
    for bot in roster:
        # Default to unlocked unless explicitly locked
        if not bot.get("unlocked", True):
            # Unlock by affection
            if bot.get("affection", 0) >= 10:  # example threshold
                bot["unlocked"] = True
                print(f"🎉 {bot['name']} has been unlocked through affection!")

            # Unlock by milestone
            elif "Chatted with {}".format(bot["name"]) in user_state.get("milestones", []):
                bot["unlocked"] = True
                print(f"🎉 {bot['name']} has been unlocked through milestones!")