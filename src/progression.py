def check_unlocks(user_state, roster):
    # Example: unlock new bots after milestones
    for bot in roster:
        if not bot.get("unlocked", True):
            # Replace with real milestone logic
            if "starter" in user_state:
                bot["unlocked"] = True
                print(f"🎉 {bot['name']} has been unlocked!")