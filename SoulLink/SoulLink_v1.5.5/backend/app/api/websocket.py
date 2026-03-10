# /backend/app/api/websocket.py
# v1.5.5 - WebSocket API Endpoint
# "Real-time is the new black." - Unknown

"""
WebSocket API Router
Handles WebSocket connections with JWT authentication.
Thin API layer - business logic is in websocket_manager service.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from backend.app.services.websocket_manager import websocket_manager
from backend.app.api.dependencies import supabase
import logging
import json

router = APIRouter(prefix="/ws", tags=["WebSocket"])
logger = logging.getLogger("WebSocketAPI")

@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token")
):
    """
    WebSocket connection endpoint with JWT authentication.
    
    Connection URL: ws://localhost:8000/api/v1/ws/connect?token=<jwt>
    
    Events sent to client:
    - connection_established: Welcome message
    - chat_message: New chat response
    - location_update: Soul moved
    - intimacy_update: Relationship changed
    - time_advance: Time slot changed
    - system_notification: General alerts
    """
    
    # 1. Authenticate user
    try:
        if not supabase:
            await websocket.close(code=1011, reason="Server configuration error")
            return
        
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            await websocket.close(code=1008, reason="Invalid authentication token")
            logger.warning("WebSocket auth failed: Invalid token")
            return
        
        user_id = user_response.user.id
        
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=1011, reason="Authentication failed")
        return
    
    # 2. Connect and register
    await websocket_manager.connect(websocket, user_id)
    
    try:
        # 3. Listen for client messages (heartbeat, subscriptions, etc.)
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Handle client messages
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })
                
                elif message.get("type") == "subscribe":
                    # Future: Handle topic subscriptions (e.g., specific souls, locations)
                    logger.info(f"User {user_id} subscribed to: {message.get('topic')}")
                
                else:
                    logger.warning(f"Unknown message type from {user_id}: {message.get('type')}")
            
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from {user_id}: {data}")
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally: {user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
    
    finally:
        # 4. Cleanup
        websocket_manager.disconnect(websocket)


@router.get("/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics.
    Useful for monitoring and debugging.
    """
    return {
        "total_connections": websocket_manager.get_connection_count(),
        "unique_users": websocket_manager.get_user_count()
    }
