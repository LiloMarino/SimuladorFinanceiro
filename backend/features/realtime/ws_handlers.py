import logging
from http.cookies import SimpleCookie
from uuid import UUID

from socketio import AsyncServer

from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import get_socket_broker

logger = logging.getLogger(__name__)


def register_ws_handlers(sio: AsyncServer):
    async def _extract_client_id(environ) -> UUID | None:
        cookies = SimpleCookie(environ.get("HTTP_COOKIE", ""))
        client = cookies.get("client_id")
        return UUID(client.value) if client else None

    @sio.event
    async def connect(sid, environ):  # type: ignore
        broker = get_socket_broker()
        client_id = await _extract_client_id(environ)
        # Recusa conexão se não tiver client_id
        if not client_id:
            logger.warning("WS connection rejected (no client_id)")
            return False

        broker.register_client(client_id, sid)
        UserManager.register(client_id)

        logger.info(f"WS client connected: {client_id} (sid={sid})")
        return True

    @sio.event
    async def disconnect(sid):  # type: ignore
        broker = get_socket_broker()
        client_id = broker.get_client_id_by_sid(sid)

        if client_id:
            broker.remove_client(client_id, sid)
            UserManager.unregister(client_id)
            logger.info(f"WS client disconnected: {client_id} (sid={sid})")

    @sio.event
    async def subscribe(sid, data):  # type: ignore
        broker = get_socket_broker()
        client_id = broker.get_client_id_by_sid(sid)

        if not client_id:
            return

        events = data.get("events", [])
        broker.update_subscription(client_id, events)

        await sio.emit("subscribed", {"events": events}, to=sid)
        logger.info(f"WS client subscribed: {client_id} -> {events}")
