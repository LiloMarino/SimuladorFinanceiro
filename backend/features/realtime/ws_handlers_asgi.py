import socketio

from backend.core.logger import setup_logger
from backend.core.runtime.user_manager import UserManager

logger = setup_logger(__name__)


def register_ws_handlers(sio: socketio.AsyncServer):
    """Register WebSocket handlers for ASGI SocketIO server."""

    @sio.event
    async def connect(sid, environ):
        """Handle client connection."""
        # Get cookies from environ
        cookie_header = environ.get("HTTP_COOKIE", "")
        cookies = {}
        for cookie in cookie_header.split("; "):
            if "=" in cookie:
                key, value = cookie.split("=", 1)
                cookies[key] = value

        client_id = cookies.get("client_id")

        # Refuse connection if no client_id
        if not client_id:
            logger.warning(f"Connection refused: no client_id (sid={sid})")
            return False

        # Get broker from the app - we'll import it here to avoid circular imports
        from main_fastapi import get_socket_broker

        broker = get_socket_broker()
        broker.register_client(client_id, sid)
        UserManager.register(client_id)
        logger.info(f"WS client connected: {client_id} (sid={sid})")
        return True

    @sio.event
    async def disconnect(sid):
        """Handle client disconnection."""
        # We need to find the client_id from the registered clients
        from main_fastapi import get_socket_broker

        broker = get_socket_broker()

        # Find client_id by sid
        client_id = None
        for cid, sids in broker._client_to_sids.items():
            if sid in sids:
                client_id = cid
                break

        if client_id:
            broker.remove_client(client_id, sid)
            UserManager.unregister(client_id)
            logger.info(f"WS client disconnected: {client_id} (sid={sid})")

    @sio.event
    async def subscribe(sid, data):
        """Handle subscription updates."""
        # Get cookies to find client_id
        from main_fastapi import get_socket_broker

        broker = get_socket_broker()

        # Find client_id by sid
        client_id = None
        for cid, sids in broker._client_to_sids.items():
            if sid in sids:
                client_id = cid
                break

        if not client_id:
            return

        events = data.get("events", [])
        broker.update_subscription(client_id, events)
        await sio.emit("subscribed", {"events": events}, to=sid)
        logger.info(f"WS client subscribed: {client_id} -> {events}")
