# main.py
from roster_loader import load_roster
from chat_engine import start_chat
from onboarding import start_onboarding
from progression import check_unlocks

def main():
    print("✨ Welcome to SoulLink ✨")
    print("Forge your bond with a companion from the roster below:\n")

    # Load roster
    roster = load_roster()
    if not roster:
        print("No companions available. Please check your roster file.")
        return

    # Run onboarding (starter character, preferences, etc.)
    user_state = start_onboarding()

    # Main loop: allow multiple chats until user quits
    while True:
        print("\nAvailable Companions:")
        for i, bot in enumerate(roster, 1):
            status = "Unlocked" if bot.get("unlocked", True) else "Locked"
            print(f"{i}. {bot['name']} ({bot['archetype']}) - {status}")

        choice = input("\nChoose a companion (number) or 'q' to quit: ")
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

            # Start chat session
            start_chat(selected_bot, user_state)

            # After chat, check progression milestones
            check_unlocks(user_state, roster)

        except ValueError:
            print("Invalid choice, please enter a valid number.")

if __name__ == "__main__":
    main()