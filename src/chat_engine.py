import random

def start_chat(bot, user_state=None):
    profile = user_state.get("profile", {}) if user_state else {}
    username = profile.get("name", "Traveler")
    age = profile.get("age", None)
    gender = profile.get("gender", None)

    print(f"\n--- Chatting with {bot['name']} ({bot['archetype']}) ---")
    print("Type 'exit' to end.\n")

    traits = bot.get("personality", {}).get("traits", [])
    flaws = bot.get("personality", {}).get("flaws", [])
    quotes = bot.get("voice", {}).get("quotes", [])
    responses = bot.get("responses", {})

    while True:
        msg = input(f"{username}: ")
        if msg.lower() == "exit":
            farewell = responses.get("Farewell", [f"Until our souls link again, {username}..."])
            print(f"{bot['name']}: {random.choice(farewell)}")
            break

        response = generate_response(bot, msg, username, age, gender, traits, flaws, quotes, responses)
        print(response)

        # Track progression milestones
        if user_state is not None:
            milestone = f"Chatted with {bot['name']}"
            if milestone not in user_state.get("milestones", []):
                user_state.setdefault("milestones", []).append(milestone)
                print(f"🎉 Milestone achieved: {milestone}")

            # Increment affection
            bot["affection"] = bot.get("affection", 0) + 1
            print(f"💖 Affection with {bot['name']} is now {bot['affection']}")

def generate_response(bot, msg, username, age, gender, traits, flaws, quotes, responses):
    """
    Smarter response logic:
    - Keyword triggers (sad, happy, love, etc.)
    - Personality-driven templates
    - Profile-aware personalization
    - Random fallback to quotes, traits, flaws, or responses
    """
    msg_lower = msg.lower()

    # Keyword triggers
    if "sad" in msg_lower and traits:
        return f"{bot['name']}: I can sense your mood, {username}. Even with my {random.choice(traits)}, I want to lift you up."
    elif "happy" in msg_lower:
        return f"{bot['name']}: Your joy is contagious, {username}! It makes my {bot['archetype']} heart shine."
    elif "love" in msg_lower:
        return f"{bot['name']}: Love is complicated... but I feel something when you say that, {username}."

    # Profile-aware personalization
    if age and random.random() < 0.3:
        return f"{bot['name']}: At {age}, you already carry wisdom, {username}."
    if gender and random.random() < 0.3:
        return f"{bot['name']}: I sense strength in you as a {gender}, {username}."

    # Trait-driven fallback
    if traits and random.random() < 0.4:
        trait = random.choice(traits)
        return f"{bot['name']}: As someone who's {trait}, I'd say '{msg}' stirs something in me."

    # Flaw-driven fallback
    if flaws and random.random() < 0.2:
        flaw = random.choice(flaws)
        return f"{bot['name']}: I admit, my {flaw} side makes it hard to answer... but I hear you, {username}."

    # Responses fallback
    if responses and random.random() < 0.5:
        default_lines = responses.get("Default", [])
        if default_lines:
            return f"{bot['name']}: {random.choice(default_lines)}"

    # Quote fallback
    if quotes and random.random() < 0.5:
        return f"{bot['name']}: {random.choice(quotes)}"

    # Generic fallback
    return f"{bot['name']}: I hear you, {username}. '{msg}' stays with me."