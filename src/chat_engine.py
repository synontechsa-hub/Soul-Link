import random

def start_chat(bot, user_state=None):
    print(f"\n--- Chatting with {bot['name']} ({bot['archetype']}) ---")
    print("Type 'exit' to end.\n")

    traits = bot.get("personality", {}).get("traits", [])
    quotes = bot.get("voice", {}).get("quotes", [])

    while True:
        msg = input("You: ")
        if msg.lower() == "exit":
            print(f"{bot['name']}: Until our souls link again...")
            break

        # Personality-flavored response
        if quotes:
            response = random.choice(quotes)
        elif traits:
            trait = random.choice(traits)
            response = f"As someone who's {trait}, I'd say: '{msg}' sparks something in me."
        else:
            response = f"{bot['name']}: Echoing '{msg}' for now."

        print(response)

        # Track progression milestones if user_state is provided
        if user_state is not None:
            milestone = f"Chatted with {bot['name']}"
            if milestone not in user_state.get("milestones", []):
                user_state.setdefault("milestones", []).append(milestone)
                print(f"🎉 Milestone achieved: {milestone}")