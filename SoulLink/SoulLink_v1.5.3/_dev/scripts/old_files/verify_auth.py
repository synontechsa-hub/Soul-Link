import requests
import os
from dotenv import load_dotenv

# Load env from backend/.env
# Note: You need a valid Supabase JWT for this to work.
# This script is a template for manual verification.

load_dotenv("backend/.env")

BASE_URL = "http://localhost:8000/api/v1"
TEST_TOKEN = os.getenv("TEST_JWT_TOKEN") # Add this to .env to test

def test_get_me():
    if not TEST_TOKEN:
        print("⚠️ TEST_JWT_TOKEN not set in .env. Skipping.")
        return

    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }

    try:
        print(f"Testing /users/me with token...")
        res = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if res.status_code == 200:
            print("✅ Auth Success:", res.json())
        else:
            print(f"❌ Auth Failed ({res.status_code}):", res.text)
    except Exception as e:
        print("❌ Connection Error:", e)

if __name__ == "__main__":
    test_get_me()
