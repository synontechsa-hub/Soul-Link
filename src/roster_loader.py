# Python-style pseudocode
from roster import load_roster
from onboarding import start_onboarding
from chat import ChatUI

def main():
    roster = load_roster("characters.json")
    user_state = start_onboarding()
    chat = ChatUI(roster, user_state)
    chat.run()

if __name__ == "__main__":
    main()