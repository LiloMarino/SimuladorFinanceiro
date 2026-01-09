"""
ASGI-compatible WebSocket event handlers for FastAPI.
This replaces the Flask-SocketIO handlers with python-socketio ASGI handlers.
"""

import socketio

from backend.core.logger import setup_logger
from backend.core.runtime.user_manager import UserManager

logger = setup_logger(__name__)


def register_async_ws_handlers(sio: socketio.AsyncServer, broker):
    """
    Register WebSocket event handlers with the ASGI socketio server.

    Args:
        sio: The AsyncServer instance
        broker: The AsyncSocketBroker instance
    """

    @sio.event
    async def connect(sid, environ, auth):
        """Handle client connection."""
        # Extract client_id from cookies
        cookies = environ.get("HTTP_COOKIE", "")
        client_id = None
        for cookie in cookies.split(";"):
            cookie = cookie.strip()
            if cookie.startswith("client_id="):
                client_id = cookie.split("=", 1)[1]
                break

        # Reject connection if no client_id
        if not client_id:
            logger.warning(f"Connection rejected: no client_id (sid={sid})")
            return False

        broker.register_client(client_id, sid)
        UserManager.register(client_id)
        logger.info(f"WS client connected: {client_id} (sid={sid})")
        return True

    @sio.event
    async def disconnect(sid):
        """Handle client disconnection."""
        # We need to track which client_id this sid belongs to
        # This is a limitation - we'll need to store sid->client_id mapping
        # For now, we rely on the broker to clean up
        logger.info(f"WS client disconnected: (sid={sid})")

    @sio.event
    async def subscribe(sid, data):
        """Handle subscription updates."""
        # Get client_id from stored mapping
        # This requires the broker to expose a way to get client_id from sid
        events = data.get("events", [])
        # For now, we'll need to pass client_id in the subscribe message
        client_id = data.get("client_id")

        if not client_id:
            logger.warning(f"Subscribe without client_id (sid={sid})")
            return

        broker.update_subscription(client_id, events)
        await sio.emit("subscribed", {"events": events}, to=sid)
        logger.info(f"WS client subscribed: {client_id} -> {events}")
