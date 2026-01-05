# main.py (ASCII Explore pre-alpha)
from roster_loader import load_roster
from chat_engine import start_chat
from onboarding import start_onboarding
from progression import check_unlocks

def show_explore(roster):
    print("\n==============================================================")
    print("✨ SoulLink — Explore Companions ✨")
    print("==============================================================")

    for i, bot in enumerate(roster, 1):
        status = "Unlocked" if bot.get("unlocked", True) else "Locked 🔒"
        traits = ", ".join(bot.get("personality", {}).get("traits", []))
        quote = bot.get("voice", {}).get("quotes", [""])[0]

        print(f"[{i}] {bot['name']} ({bot['archetype']}) — {status}")
        if traits:
            print(f"    Traits: {traits}")
        if quote:
            print(f"    Voice: \"{quote}\"")
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
        show_explore(roster)
        choice = input("\nChoose a companion (number), or 'q' to quit: ")

        if choice.lower() == 'q':
            print("\nThanks for linking souls today. See you next time!")
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
            print(f"  Traits: {traits}")
            if flaws:
                print(f"  Flaws: {flaws}")
            if quotes:
                print("  Quotes:")
                for q in quotes[:2]:
                    print(f"    - {q}")
            print("--------------------------------------------------------------")

            # Start chat
            start_chat(selected_bot, user_state)

            # Progression check
            check_unlocks(user_state, roster)

        except ValueError:
            print("Invalid choice, please enter a valid number.")

if __name__ == "__main__":
    main()