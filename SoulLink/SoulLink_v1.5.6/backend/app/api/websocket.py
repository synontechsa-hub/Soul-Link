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
from backend.app.core.config import settings
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
    Added strict IP rate limiting before connection acceptance.
    """
    from backend.app.core.rate_limiter import get_real_ip
    from backend.app.core.cache import cache_service

    client_ip = get_real_ip(websocket)  # type: ignore

    # 0. RATE LIMITING (Per-IP connection spam protection)
    # Using CacheService directly since slowapi @limiter doesn't cleanly reject unaccepted WebSockets
    rl_key = f"ws:rate_limit:{client_ip}"
    current_count = cache_service.get(rl_key) or 0
    if current_count >= 30:  # 30 connection attempts per minute max
        logger.warning("Rate limit exceeded for WS connect from %s", client_ip)
        await websocket.close(code=1008, reason="Rate Limit Exceeded")
        return

    # Needs to be a bit careful setting ttl if key doesn't exist, but our simple cache handles it
    cache_service.set(rl_key, current_count + 1, ttl=60)

    await websocket.accept()
    user_id = None

    # 1. AUTH HANDSHAKE (Strictly requires Message Handshake, no query-param leak)
    logger.info("WebSocket waiting for handshake message: %s", client_ip)
    try:
        handshake_data = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
        payload = json.loads(handshake_data)
        if payload.get("type") == "handshake" and "token" in payload:
            token = payload["token"]
        else:
            logger.warning("Invalid WebSocket handshake from %s", client_ip)
            await websocket.close(code=1008, reason="Handshake Required")
            return
    except asyncio.TimeoutError:
        logger.warning("WebSocket handshake timeout from %s", client_ip)
        await websocket.close(code=1008, reason="Handshake Timeout")
        return
    except Exception as e:
        logger.error("WebSocket handshake error: %s", e)
        await websocket.close(code=1011, reason="Handshake Failed")
        return

    # Verify Token
    if not supabase and not (settings.environment == "development" and token == "dev_mock_token_123"):
        await websocket.close(code=1011, reason="Server configuration error")
        return

    try:
        user_id = None
        # [DEV BYPASS] Let mock token through
        if settings.environment == "development" and token == "dev_mock_token_123":
            user_id = settings.architect_uuid or "14dd612d-744e-487d-b2d5-cc47732183d3"
        else:
            # Run blocking Supabase call in thread pool
            loop = asyncio.get_running_loop()
            user_response = await loop.run_in_executor(None, supabase.auth.get_user, token)

            if not user_response or not user_response.user:
                logger.warning("WebSocket auth failed from %s", client_ip)
                await websocket.close(code=1008, reason="Invalid authentication token")
                return
            user_id = user_response.user.id
            
        logger.info("WebSocket auth success: user=%s ip=%s",
                    user_id, client_ip)
    except Exception as e:
        logger.error("Supabase Auth Error in WebSocket: %s", e)
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
                logger.warning(
                    "WebSocket heartbeat timeout for user=%s. Closing.", user_id)
                await websocket.close(code=1001, reason="Heartbeat timeout")
                break

            try:
                message = json.loads(str(data))

                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })

                elif message.get("type") == "subscribe":
                    topic = message.get("topic", "unknown")
                    logger.info("User %s subscribed to: %s", user_id, topic)

                else:
                    logger.debug(
                        "Unknown WS message type from %s: %s", user_id, message.get('type'))

            except json.JSONDecodeError:
                logger.warning("Invalid JSON from %s: %s", user_id, data[:100])

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected normally: user=%s", user_id)

    except Exception as e:
        logger.error(
            "WebSocket error for user=%s: %s: %s", user_id, type(e).__name__, e)

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
