"""
WebSocket Handler

Handles real-time communication for workflow progress updates.
"""

import json
import asyncio
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections and subscriptions."""

    def __init__(self):
        # session_id -> set of websocket connections
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
        # websocket -> set of subscribed session_ids
        self.connections: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.connections[websocket] = set()

    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection."""
        # Unsubscribe from all sessions
        if websocket in self.connections:
            for session_id in self.connections[websocket]:
                if session_id in self.subscriptions:
                    self.subscriptions[session_id].discard(websocket)
            del self.connections[websocket]

    def subscribe(self, session_id: str, websocket: WebSocket):
        """Subscribe a connection to a session."""
        if session_id not in self.subscriptions:
            self.subscriptions[session_id] = set()
        self.subscriptions[session_id].add(websocket)

        if websocket in self.connections:
            self.connections[websocket].add(session_id)

    def unsubscribe(self, session_id: str, websocket: WebSocket):
        """Unsubscribe a connection from a session."""
        if session_id in self.subscriptions:
            self.subscriptions[session_id].discard(websocket)

        if websocket in self.connections:
            self.connections[websocket].discard(session_id)

    async def broadcast(self, session_id: str, message: dict):
        """Broadcast a message to all subscribers of a session."""
        if session_id not in self.subscriptions:
            return

        disconnected = []
        for websocket in self.subscriptions[session_id]:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(ws)

    async def send_to_session(self, session_id: str, event_type: str, data: dict):
        """Send an event to all subscribers of a session."""
        await self.broadcast(session_id, {
            "type": event_type,
            "sessionId": session_id,
            **data,
        })


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.

    Client messages:
    - {"type": "subscribe", "sessionId": "..."}
    - {"type": "unsubscribe", "sessionId": "..."}

    Server messages:
    - {"type": "subscribed", "sessionId": "..."}
    - {"type": "phase_changed", "sessionId": "...", "phase": "...", "data": {...}}
    - {"type": "approval_required", "sessionId": "...", "approvalType": "...", "data": {...}}
    - {"type": "progress", "sessionId": "...", "message": "...", "progress": 0.5}
    - {"type": "error", "sessionId": "...", "message": "..."}
    - {"type": "completed", "sessionId": "...", "summary": {...}}
    - {"type": "video_status", "sessionId": "...", "shotId": "...", "status": "...", "url": "..."}
    """
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "subscribe":
                session_id = data.get("sessionId")
                if session_id:
                    manager.subscribe(session_id, websocket)
                    await websocket.send_json({
                        "type": "subscribed",
                        "sessionId": session_id,
                    })

            elif msg_type == "unsubscribe":
                session_id = data.get("sessionId")
                if session_id:
                    manager.unsubscribe(session_id, websocket)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "sessionId": session_id,
                    })

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)


# Helper functions for sending notifications from other parts of the app

async def notify_phase_changed(session_id: str, phase: str, data: dict = None):
    """Notify subscribers that the workflow phase has changed."""
    await manager.send_to_session(session_id, "phase_changed", {
        "phase": phase,
        "data": data or {},
    })


async def notify_approval_required(session_id: str, approval_type: str, data: dict = None):
    """Notify subscribers that approval is required."""
    await manager.send_to_session(session_id, "approval_required", {
        "approvalType": approval_type,
        "data": data or {},
    })


async def notify_progress(session_id: str, message: str, progress: float = 0):
    """Notify subscribers of progress update."""
    await manager.send_to_session(session_id, "progress", {
        "message": message,
        "progress": progress,
    })


async def notify_error(session_id: str, message: str):
    """Notify subscribers of an error."""
    await manager.send_to_session(session_id, "error", {
        "message": message,
    })


async def notify_completed(session_id: str, summary: dict):
    """Notify subscribers that the workflow is completed."""
    await manager.send_to_session(session_id, "completed", {
        "summary": summary,
    })


async def notify_video_status(session_id: str, shot_id: str, status: str, url: str = None):
    """Notify subscribers of video generation status update."""
    await manager.send_to_session(session_id, "video_status", {
        "shotId": shot_id,
        "status": status,
        "url": url,
    })
