# main.py (ASCII Explore with affection + card unlocks)
from roster_loader import load_roster
from chat_engine import start_chat
from onboarding import start_onboarding
from progression import check_unlocks

def get_card_preview(bot):
    """Return the appropriate card based on affection score."""
    cards = bot.get("cards", [])
    affection = bot.get("affection", 0)

    if not cards:
        return None

    # Example: unlock second card at affection >= 20
    if affection >= 20 and len(cards) > 1:
        return cards[1]
    return cards[0]

def show_explore(roster, user_state):
    print("\n==============================================================")
    username = user_state.get("profile", {}).get("name", "Traveler")
    print(f"✨ SoulLink — Explore Companions for {username} ✨")
    print("==============================================================")

    for i, bot in enumerate(roster, 1):
        status = "Unlocked" if bot.get("unlocked", True) else "Locked 🔒"

        name = bot.get("name", "Unknown")
        archetype = bot.get("archetype", "Unknown")
        traits = ", ".join(bot.get("personality", {}).get("traits", []))
        quotes = bot.get("voice", {}).get("quotes", [])
        quote = quotes[0] if quotes else ""
        affection = bot.get("affection", 0)
        card_preview = get_card_preview(bot)

        print(f"[{i}] {name} ({archetype}) — {status}")
        if traits:
            print(f"    Traits: {traits}")
        if quote:
            print(f"    Voice: \"{quote}\"")
        print(f"    Affection: {affection} ❤️")
        if card_preview:
            print(f"    Card preview: {card_preview}")
        print("    ------------------------------------")
        if status == "Unlocked":
            print("    [Start Chat]  [Preview Quotes]  [Pin]")
        else:
            print("    [Unlock Hint: Progress further]")
        print()

def main():
    print("✨ Welcome to SoulLink ✨")
    print("Forge your bond with a companion from the roster below:\n")

    roster = load_roster()
    if not roster:
        print("No companions available. Please check your roster files.")
        return

    user_state = start_onboarding()

    while True:
        show_explore(roster, user_state)
        choice = input("\nChoose a companion (number), or 'q' to quit: ")

        if choice.lower() == 'q':
            print(f"\nThanks for linking souls today, {user_state['profile']['name']}. See you next time!")
            break

        try:
            choice_index = int(choice) - 1
            if choice_index < 0 or choice_index >= len(roster):
                raise ValueError

            selected_bot = roster[choice_index]
            if not selected_bot.get("unlocked", True):
                print(f"{selected_bot['name']} is locked. Progress further to unlock this companion.")
                continue

            # ASCII detail view
            print("\n--------------------------------------------------------------")
            print(f"> {selected_bot['name']} — {selected_bot['archetype']}")
            traits = ", ".join(selected_bot.get("personality", {}).get("traits", []))
            flaws = ", ".join(selected_bot.get("personality", {}).get("flaws", []))
            quotes = selected_bot.get("voice", {}).get("quotes", [])
            affection = selected_bot.get("affection", 0)
            card_preview = get_card_preview(selected_bot)

            if traits:
                print(f"  Traits: {traits}")
            if flaws:
                print(f"  Flaws: {flaws}")
            if quotes:
                print("  Quotes:")
                for q in quotes[:2]:
                    print(f"    - {q}")
            print(f"  Affection: {affection} ❤️")
            if card_preview:
                print(f"  Card preview: {card_preview}")
            print("--------------------------------------------------------------")

            # Start chat
            start_chat(selected_bot, user_state)

            # Progression check
            check_unlocks(user_state, roster)

        except ValueError:
            print("Invalid choice, please enter a valid number.")

if __name__ == "__main__":
    main()