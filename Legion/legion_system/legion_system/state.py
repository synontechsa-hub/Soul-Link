import reflex as rx
import json
import asyncio
import websockets

class LegionState(rx.State):
    """The app state for Mission Control."""
    gateway_status: str = "Disconnected"
    logs: list[str] = ["System Initialization sequence started...", "Awaiting Gateway Link."]
    active_agent: str = "None"
    
    async def connect_to_openclaw(self):
        """Connects to OpenClaw's WebSocket Gateway in the background using yields."""
        self.gateway_status = "Connecting..."
        self.logs.append("Attempting WS connection to 127.0.0.1:18789...")
        yield
            
        try:
            async with websockets.connect("ws://127.0.0.1:18789") as websocket:
                self.gateway_status = "Connected"
                self.logs.append("✅ Gateway Link Established.")
                yield
                
                while True:
                    try:
                        message = await websocket.recv()
                        # Try to parse JSON to pretty-print or just append raw
                        try:
                            data = json.loads(message)
                            
                            # Handle OpenClaw Handshake (ACP)
                            if data.get("type") == "event" and data.get("event") == "connect.challenge":
                                self.logs.append("⚠️ Handshake Challenge Received. Authenticating...")
                                yield
                                
                                response_payload = {
                                    "type": "req",
                                    "id": str(data.get("payload", {}).get("nonce", "legion-auth")),
                                    "method": "connect",
                                    "params": {
                                        "minProtocol": 3,
                                        "maxProtocol": 3,
                                        "client": {
                                            "id": "openclaw-control-ui",
                                            "version": "dev",
                                            "platform": "web",
                                            "mode": "webchat"
                                        },
                                        "role": "operator",
                                        "scopes": ["operator.admin", "operator.approvals", "operator.pairing"],
                                        "caps": [],
                                        "auth": {
                                            "token": "legion-mission-control" 
                                        }
                                    }
                                }
                                await websocket.send(json.dumps(response_payload))
                                self.logs.append("✅ Sent Authentication Response!")
                                yield
                                
                            line = f"[{data.get('event', data.get('type', 'MSG'))}] {json.dumps(data)}"
                        except:
                            line = f"[RAW] {message}"
                            
                        self.logs.append(line)
                        if len(self.logs) > 100:
                            self.logs.pop(0)
                        yield
                    except websockets.exceptions.ConnectionClosed:
                        self.gateway_status = "Disconnected"
                        self.logs.append("❌ Gateway Link Lost.")
                        yield
                        break
        except Exception as e:
            self.gateway_status = f"Error: {e}"
            self.logs.append(f"❌ Connection failed: {e}")
            yield
