# chat_with_soul.py
# Terminal chat client for SoulLink backend API
# Usage: python chat_with_soul.py --soul_id rosalynn --user_id syn_01

import requests
import argparse
import sys
import time
from typing import List, Dict

# ────────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────────

API_BASE_URL = "http://127.0.0.1:8000/api/v1/chat"  # Change if your port/host is different

# ────────────────────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────────────────────

def clear_screen():
    print("\033[H\033[J", end="")  # ANSI clear

def print_header(soul_id: str, user_id: str):
    print("═" * 70)
    print(f"  SoulLink Chat: {soul_id.capitalize()}  (as {user_id})  ".center(70, "═"))
    print("═" * 70)
    print("  Type your message and press Enter.")
    print("  Commands: /soul <id> to switch soul, /exit or Ctrl+C to quit.\n")

def format_message(role: str, content: str, soul_name: str) -> str:
    if role == "user":
        return f"\033[38;5;45mYou:\033[0m {content}"
    elif role == "assistant":
        return f"\033[38;5;141m{soul_name}:\033[0m {content}"
    return content

def send_message(soul_id: str, user_id: str, message: str, history: List[Dict]) -> str:
    try:
        response = requests.post(
            f"{API_BASE_URL}/{soul_id}",
            params={"user_id": user_id, "message": message},
            headers={"accept": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get("reply", "No reply received.")
    except requests.exceptions.RequestException as e:
        return f"[Error: {str(e)}] Connection to Link City failed."

# ────────────────────────────────────────────────────────────────
# MAIN CHAT LOOP
# ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Chat with souls via SoulLink API")
    parser.add_argument("--soul_id", type=str, default="rosalynn", help="Soul ID to chat with")
    parser.add_argument("--user_id", type=str, default="syn_01", help="Your user ID")

    args = parser.parse_args()

    current_soul = args.soul_id
    user_id = args.user_id
    history: List[Dict[str, str]] = []  # We'll append user/assistant pairs

    clear_screen()
    print_header(current_soul, user_id)

    print(format_message("assistant", "The connection is stable. I am listening.", current_soul.capitalize()))
    print()

    while True:
        try:
            user_input = input("\033[38;5;45m> \033[0m").strip()

            if not user_input:
                continue

            # ─── Commands ─────────────────────────────────────────────
            if user_input.lower().startswith("/soul "):
                new_soul = user_input[6:].strip()
                if new_soul:
                    current_soul = new_soul
                    print(f"\n[Switched to {current_soul.capitalize()}]")
                    history = []  # Reset history on soul switch
                    print_header(current_soul, user_id)
                continue

            if user_input.lower() in ("/exit", "/quit", "exit", "quit"):
                print("\nGoodbye… maybe we'll talk again.")
                break
          
            print(f"\033[38;5;141m{current_soul.capitalize()}:\033[0m ", end="", flush=True)

            reply = send_message(current_soul, user_id, user_input, history)

            # Typewriter effect
            for char in reply:
                print(char, end="", flush=True)
                time.sleep(0.012)  # Adjust for typing speed

            print()  # newline
            print()

            # Store in history (for future context if you extend)
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": reply})

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye for now…")
            break
        except Exception as e:
            print(f"\n[Unexpected error]: {e}")
            print("Trying to continue…")

if __name__ == "__main__":
    main()