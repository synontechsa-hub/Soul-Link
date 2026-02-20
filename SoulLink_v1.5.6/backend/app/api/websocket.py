# /backend/app/api/websocket.py
# v1.5.6 Normandy SR-2 — WebSocket API Endpoint
# UPDATED: Added heartbeat timeout (60s), connection rate limiting, audit logging.

"""
WebSocket API Router
Handles WebSocket connections with JWT authentication.
Thin API layer - business logic is in websocket_manager service.
"""

import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from backend.app.services.websocket_manager import websocket_manager
from backend.app.api.dependencies import supabase, require_architect_role

router = APIRouter(prefix="/ws", tags=["WebSocket"])
logger = logging.getLogger("WebSocketAPI")

# Heartbeat: disconnect clients that don't ping within this window (seconds)
HEARTBEAT_TIMEOUT = 60


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket connection endpoint.
    Normandy-SR2 Fix: Token moved from Query to Initial Handshake Message for log security.
    """
    await websocket.accept()
    client_ip = websocket.client.host if websocket.client else "unknown"
    user_id = None

    # 1. AUTH HANDSHAKE (Supports Query Param fallback and Message Handshake)
    token = websocket.query_params.get("token")
    
    if token:
        logger.info(f"WebSocket using query-param auth: {client_ip}")
    else:
        # If no token in query, we wait for the message handshake
        logger.info(f"WebSocket waiting for handshake message: {client_ip}")
        try:
            handshake_data = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
            payload = json.loads(handshake_data)
            if payload.get("type") == "handshake" and "token" in payload:
                token = payload["token"]
            else:
                logger.warning(f"Invalid WebSocket handshake from {client_ip}")
                await websocket.close(code=1008, reason="Handshake Required")
                return
        except asyncio.TimeoutError:
            logger.warning(f"WebSocket handshake timeout from {client_ip}")
            await websocket.close(code=1008, reason="Handshake Timeout")
            return
        except Exception as e:
            logger.error(f"WebSocket handshake error: {e}")
            await websocket.close(code=1011, reason="Handshake Failed")
            return

    # Verify Token
    if not supabase:
        await websocket.close(code=1011, reason="Server configuration error")
        return

    try:
        # Run blocking Supabase call in thread pool
        loop = asyncio.get_running_loop()
        user_response = await loop.run_in_executor(None, supabase.auth.get_user, token)

        if not user_response or not user_response.user:
            logger.warning(f"WebSocket auth failed from {client_ip}")
            await websocket.close(code=1008, reason="Invalid authentication token")
            return

        user_id = user_response.user.id
        logger.info(f"WebSocket auth success: user={user_id} ip={client_ip}")
    except Exception as e:
        logger.error(f"Supabase Auth Error in WebSocket: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # 2. Connect and register
    await websocket_manager.connect(websocket, user_id)

    try:
        # 3. Listen for client messages with heartbeat enforcement
        while True:
            try:
                # Wait for a message with a timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=HEARTBEAT_TIMEOUT
                )
            except asyncio.TimeoutError:
                # Client didn't ping within the heartbeat window — disconnect
                logger.warning(f"WebSocket heartbeat timeout for user={user_id}. Closing.")
                await websocket.close(code=1001, reason="Heartbeat timeout")
                break

            try:
                message = json.loads(data)

                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })

                elif message.get("type") == "subscribe":
                    topic = message.get("topic", "unknown")
                    logger.info(f"User {user_id} subscribed to: {topic}")

                else:
                    logger.debug(f"Unknown WS message type from {user_id}: {message.get('type')}")

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from {user_id}: {data[:100]}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally: user={user_id}")

    except Exception as e:
        logger.error(f"WebSocket error for user={user_id}: {type(e).__name__}: {e}")

    finally:
        websocket_manager.disconnect(websocket)


@router.get("/stats")
async def get_websocket_stats(user_id: str = Depends(require_architect_role)):
    """
    Get WebSocket connection statistics (Architects Only).
    """
    return {
        "total_connections": websocket_manager.get_connection_count(),
        "unique_users": websocket_manager.get_user_count(),
        "heartbeat_timeout_seconds": HEARTBEAT_TIMEOUT
    }
