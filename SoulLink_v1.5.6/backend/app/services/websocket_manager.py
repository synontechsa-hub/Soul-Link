# /backend/app/services/websocket_manager.py
# v1.5.5 - Real-time WebSocket Connection Management
# "The future is already here — it's just not evenly distributed." - William Gibson

"""
WebSocket Manager Service
Handles WebSocket connections, authentication, and message broadcasting.
Separated from API layer for easier debugging and testing.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional
import json
from datetime import datetime
from backend.app.core.logging_config import get_logger

logger = get_logger("WebSocketManager")

class WebSocketManager:
    """
    Centralized WebSocket connection manager.
    Handles connection lifecycle, authentication, and broadcasting.
    """
    
    MAX_CONNECTIONS_PER_USER = 5  # Prevent resource exhaustion
    
    def __init__(self):
        # Active connections: {user_id: List[WebSocket]} (FIFO order)
        self._connections: Dict[str, list[WebSocket]] = {}
        # Connection metadata: {websocket_id: user_id}
        self._connection_metadata: Dict[int, str] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """
        Register a new WebSocket connection.
        Enforces max connections per user.
        
        Args:
            websocket: The WebSocket connection
            user_id: Authenticated user ID
        """
        # Note: websocket.accept() is handled by the calling API endpoint
        
        if user_id in self._connections:
            if len(self._connections[user_id]) >= self.MAX_CONNECTIONS_PER_USER:
                # Disconnect oldest connection (FIFO: index 0)
                oldest_ws = self._connections[user_id].pop(0)
                try:
                    await oldest_ws.close(code=1008, reason="Connection limit exceeded")
                except:
                    pass
                self._connection_metadata.pop(id(oldest_ws), None)
                logger.warning(f"FIFO Eviction: Disconnected oldest for {user_id}")
        
        # Register connection
        if user_id not in self._connections:
            self._connections[user_id] = []
        
        self._connections[user_id].append(websocket)
        self._connection_metadata[id(websocket)] = user_id
        
        logger.info(f"✅ WebSocket connected: {user_id} (Total: {self.get_connection_count()})")
        
        # Send welcome message
        await self.send_to_user(user_id, {
            "type": "connection_established",
            "user_id": user_id,
            "message": "Neural Link synchronized.",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, websocket: WebSocket) -> Optional[str]:
        """
        Unregister a WebSocket connection.
        
        Args:
            websocket: The WebSocket connection to remove
            
        Returns:
            user_id if found, None otherwise
        """
        ws_id = id(websocket)
        user_id = self._connection_metadata.get(ws_id)
        
        if user_id and user_id in self._connections:
            if websocket in self._connections[user_id]:
                self._connections[user_id].remove(websocket)
            
            # Clean up empty lists
            if not self._connections[user_id]:
                del self._connections[user_id]
            
            del self._connection_metadata[ws_id]
            logger.info(f"❌ WebSocket disconnected: {user_id} (Total: {self.get_connection_count()})")
            
        return user_id
    
    async def send_to_user(self, user_id: str, message: dict) -> int:
        """
        Send message to all connections for a specific user.
        
        Args:
            user_id: Target user
            message: Message dict to send (will be JSON serialized)
            
        Returns:
            Number of successful sends
        """
        if user_id not in self._connections:
            return 0
        
        dead_indices = []
        sent_count = 0
        conns = self._connections[user_id]
        
        for i, ws in enumerate(conns):
            try:
                await ws.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to send to {user_id}: {e}")
                dead_indices.append(i)
        
        # Cleanup dead connections in reverse to maintain index integrity
        for i in sorted(dead_indices, reverse=True):
            ws = conns.pop(i)
            self._connection_metadata.pop(id(ws), None)
            
        if not self._connections[user_id]:
            del self._connections[user_id]
        
        return sent_count
    
    async def broadcast_to_all(self, message: dict) -> int:
        """
        Broadcast message to all connected users.
        
        Args:
            message: Message dict to broadcast
            
        Returns:
            Total number of successful sends
        """
        total_sent = 0
        
        for user_id in list(self._connections.keys()):
            sent = await self.send_to_user(user_id, message)
            total_sent += sent
        
        return total_sent
    
    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return sum(len(conns) for conns in self._connections.values())
    
    def get_user_count(self) -> int:
        """Get number of unique connected users."""
        return len(self._connections)
    
    def is_user_connected(self, user_id: str) -> bool:
        """Check if a user has any active connections."""
        return user_id in self._connections and len(self._connections[user_id]) > 0


# Global singleton instance
websocket_manager = WebSocketManager()
