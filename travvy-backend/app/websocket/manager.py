"""
WebSocket Connection Manager

This module handles real-time WebSocket connections for
trip collaboration and live updates.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket connection manager for real-time collaboration.
    """
    
    def __init__(self):
        # Active connections: {trip_id: {user_id: websocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # User activity tracking
        self.user_activity: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, trip_id: str, user_id: str):
        """
        Accept WebSocket connection and add to active connections.
        
        Args:
            websocket: WebSocket connection
            trip_id: Trip ID for collaboration
            user_id: User ID connecting
        """
        try:
            await websocket.accept()
            
            # Initialize trip connections if not exists
            if trip_id not in self.active_connections:
                self.active_connections[trip_id] = {}
            
            # Add connection
            self.active_connections[trip_id][user_id] = websocket
            
            # Track user activity
            if trip_id not in self.user_activity:
                self.user_activity[trip_id] = {}
            
            self.user_activity[trip_id][user_id] = {
                "status": "active",
                "last_seen": datetime.utcnow(),
                "cursor": None
            }
            
            logger.info(f"User {user_id} connected to trip {trip_id}")
            
            # Notify other users about new connection
            await self.broadcast_to_trip(
                trip_id, 
                {
                    "type": "user_joined",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "active_users": list(self.active_connections[trip_id].keys())
                },
                exclude=user_id
            )
            
        except Exception as e:
            logger.error(f"Connection failed for user {user_id} on trip {trip_id}: {str(e)}")
            raise
    
    def disconnect(self, websocket: WebSocket, trip_id: str):
        """
        Remove WebSocket connection.
        
        Args:
            websocket: WebSocket connection to remove
            trip_id: Trip ID
        """
        try:
            user_id = None
            
            # Find and remove the connection
            if trip_id in self.active_connections:
                for uid, ws in self.active_connections[trip_id].items():
                    if ws == websocket:
                        user_id = uid
                        break
                
                if user_id:
                    # Remove connection
                    del self.active_connections[trip_id][user_id]
                    
                    # Update user activity
                    if trip_id in self.user_activity and user_id in self.user_activity[trip_id]:
                        self.user_activity[trip_id][user_id]["status"] = "disconnected"
                        self.user_activity[trip_id][user_id]["last_seen"] = datetime.utcnow()
                    
                    # Clean up empty trip connections
                    if not self.active_connections[trip_id]:
                        del self.active_connections[trip_id]
                        if trip_id in self.user_activity:
                            del self.user_activity[trip_id]
                    
                    logger.info(f"User {user_id} disconnected from trip {trip_id}")
                    
                    # Notify other users about disconnection
                    if trip_id in self.active_connections:
                        asyncio.create_task(
                            self.broadcast_to_trip(
                                trip_id,
                                {
                                    "type": "user_left",
                                    "user_id": user_id,
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "active_users": list(self.active_connections[trip_id].keys())
                                },
                                exclude=user_id
                            )
                        )
                    
        except Exception as e:
            logger.error(f"Disconnection handling failed for trip {trip_id}: {str(e)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Send message to specific WebSocket connection.
        
        Args:
            message: Message to send
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {str(e)}")
    
    async def broadcast_to_trip(
        self, 
        trip_id: str, 
        message: Any, 
        exclude: Optional[str] = None
    ):
        """
        Broadcast message to all users in a trip.
        
        Args:
            trip_id: Trip ID to broadcast to
            message: Message to broadcast
            exclude: User ID to exclude from broadcast
        """
        try:
            if trip_id not in self.active_connections:
                return
            
            # Convert message to JSON if it's not a string
            if not isinstance(message, str):
                message = json.dumps(message, default=str)
            
            # Send to all connected users in the trip
            disconnected_users = []
            
            for user_id, websocket in self.active_connections[trip_id].items():
                if exclude and user_id == exclude:
                    continue
                
                try:
                    await websocket.send_text(message)
                    
                    # Update last seen
                    if trip_id in self.user_activity and user_id in self.user_activity[trip_id]:
                        self.user_activity[trip_id][user_id]["last_seen"] = datetime.utcnow()
                        
                except WebSocketDisconnect:
                    disconnected_users.append(user_id)
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {str(e)}")
                    disconnected_users.append(user_id)
            
            # Clean up disconnected users
            for user_id in disconnected_users:
                if user_id in self.active_connections[trip_id]:
                    del self.active_connections[trip_id][user_id]
            
        except Exception as e:
            logger.error(f"Broadcast failed for trip {trip_id}: {str(e)}")
    
    async def send_to_user(self, trip_id: str, user_id: str, message: Any):
        """
        Send message to specific user in a trip.
        
        Args:
            trip_id: Trip ID
            user_id: Target user ID
            message: Message to send
        """
        try:
            if (trip_id in self.active_connections and 
                user_id in self.active_connections[trip_id]):
                
                websocket = self.active_connections[trip_id][user_id]
                
                if not isinstance(message, str):
                    message = json.dumps(message, default=str)
                
                await websocket.send_text(message)
                
        except Exception as e:
            logger.error(f"Failed to send message to user {user_id} in trip {trip_id}: {str(e)}")
    
    def get_active_users(self, trip_id: str) -> List[str]:
        """
        Get list of active users in a trip.
        
        Args:
            trip_id: Trip ID
            
        Returns:
            List of active user IDs
        """
        if trip_id in self.active_connections:
            return list(self.active_connections[trip_id].keys())
        return []
    
    def get_user_activity(self, trip_id: str) -> Dict[str, Any]:
        """
        Get user activity information for a trip.
        
        Args:
            trip_id: Trip ID
            
        Returns:
            User activity data
        """
        if trip_id in self.user_activity:
            return self.user_activity[trip_id]
        return {}
    
    async def handle_cursor_update(self, trip_id: str, user_id: str, cursor_data: Dict[str, Any]):
        """
        Handle cursor position updates for collaborative editing.
        
        Args:
            trip_id: Trip ID
            user_id: User updating cursor
            cursor_data: Cursor position data
        """
        try:
            # Update user cursor position
            if (trip_id in self.user_activity and 
                user_id in self.user_activity[trip_id]):
                self.user_activity[trip_id][user_id]["cursor"] = cursor_data
            
            # Broadcast cursor update to other users
            await self.broadcast_to_trip(
                trip_id,
                {
                    "type": "cursor_update",
                    "user_id": user_id,
                    "cursor": cursor_data,
                    "timestamp": datetime.utcnow().isoformat()
                },
                exclude=user_id
            )
            
        except Exception as e:
            logger.error(f"Cursor update failed: {str(e)}")
    
    async def handle_trip_update(self, trip_id: str, user_id: str, update_data: Dict[str, Any]):
        """
        Handle real-time trip updates.
        
        Args:
            trip_id: Trip ID
            user_id: User making the update
            update_data: Update data
        """
        try:
            # Broadcast update to other users
            await self.broadcast_to_trip(
                trip_id,
                {
                    "type": "trip_update",
                    "user_id": user_id,
                    "update": update_data,
                    "timestamp": datetime.utcnow().isoformat()
                },
                exclude=user_id
            )
            
        except Exception as e:
            logger.error(f"Trip update broadcast failed: {str(e)}")


# Global connection manager instance
manager = ConnectionManager()
