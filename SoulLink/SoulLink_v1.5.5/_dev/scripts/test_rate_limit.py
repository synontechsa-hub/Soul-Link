
import asyncio
import httpx
import time

API_URL = "http://127.0.0.1:8000/api/v1"
CONCURRENT_REQUESTS = 20  # Total requests to send
DELAY = 0.05  # Delay between requests

async def ping(client, i):
    try:
        response = await client.get(f"{API_URL}/users/me")
        print(f"Req {i}: Status {response.status_code}")
        if response.status_code == 429:
            print(f"🛑 BLOCKED: {response.json()}")
            return "BLOCKED"
        elif response.status_code == 200:
            return "OK"
        else:
            print(f"❌ Error: {response.text}")
            return "ERROR"
    except Exception as e:
        print(f"⚠️ Connection Error: {e}")
        return "CONN_ERR"

async def spam_attack():
    # You MUST have the token in the script or use a public endpoint.
    # Actually, rate limits apply to IP if no auth? 
    # Current limiter uses get_remote_address.
    
    # We will hit a public endpoint (or fake auth) to trigger IP limit?
    # Or just hit /api/v1/souls/explore which is public?
    # Or map/locations.
    
    target_url = f"{API_URL}/souls/explore" 
    print(f"⚔️ Spamming {target_url}...")
    
    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(CONCURRENT_REQUESTS):
            tasks.append(client.get(target_url))
            # Just rapid fire
        
        responses = await asyncio.gather(*tasks)
        
        for i, r in enumerate(responses):
            if r.status_code == 429:
                print(f"✅ Req {i+1}: 429 SHIELD HOLDING! (Body: {r.json()['message']})")
            elif r.status_code == 200:
                print(f"Req {i+1}: 200 Passed")
            else:
                 print(f"Req {i+1}: {r.status_code}")

if __name__ == "__main__":
    asyncio.run(spam_attack())
