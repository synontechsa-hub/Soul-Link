import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_connectivity():
    print(f"📡 Testing Connectivity to {BASE_URL}...")
    
    # 1. Test Root
    try:
        resp = requests.get(f"{BASE_URL}/")
        print(f"✅ Root Endpoint: {resp.status_code} (Expected 200)")
        print(resp.json())
    except Exception as e:
        print(f"❌ Root Endpoint Failed: {e}")
        sys.exit(1)

    # 2. Test Rate Limited Endpoint (Unauthenticated)
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/users/me")
        print(f"ℹ️ /users/me (No Auth): {resp.status_code} (Expected 401)")
    except Exception as e:
        print(f"❌ /users/me Failed: {e}")

if __name__ == "__main__":
    test_connectivity()
