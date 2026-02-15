"""
WebSocket Connection Test
Tests the WebSocket endpoint with JWT authentication
"""
import asyncio
import json
import websockets
from backend.app.core.config import settings

async def test_websocket():
    """Test WebSocket connection with a mock JWT token"""
    
    # For testing, we'll use a real user token
    # You should replace this with an actual JWT from Supabase
    print("🧪 WebSocket Connection Test")
    print("=" * 50)
    
    # This is a placeholder - in real testing, you'd get this from Supabase auth
    test_token = "YOUR_JWT_TOKEN_HERE"
    
    ws_url = f"ws://127.0.0.1:8000/api/v1/ws?token={test_token}"
    
    print(f"📡 Connecting to: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ Connected!")
            
            # Send a ping
            await websocket.send(json.dumps({"type": "ping"}))
            print("📤 Sent: ping")
            
            # Wait for pong
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            print(f"📥 Received: {data}")
            
            if data.get("type") == "pong":
                print("✅ Heartbeat working!")
            
            # Keep connection alive for a bit
            print("\n⏳ Keeping connection alive for 10 seconds...")
            await asyncio.sleep(10)
            
            print("✅ Test complete!")
            
    except asyncio.TimeoutError:
        print("❌ Timeout waiting for response")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Make sure:")
        print("   1. Backend server is running")
        print("   2. You have a valid JWT token")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("\n⚠️  NOTE: This test requires a valid JWT token from Supabase")
    print("    To get one:")
    print("    1. Run the Flutter app")
    print("    2. Log in")
    print("    3. Check the console for the token (starts with 'eyJ...')")
    print("    4. Replace 'YOUR_JWT_TOKEN_HERE' in this script\n")
    
    asyncio.run(test_websocket())
