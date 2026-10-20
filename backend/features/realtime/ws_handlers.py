import logging
from http.cookies import SimpleCookie
from uuid import UUID

from socketio import AsyncServer

from backend.core.metrics import metrics
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import get_socket_broker

logger = logging.getLogger(__name__)


def register_ws_handlers(sio: AsyncServer):
    async def _extract_client_id(environ) -> UUID | None:
        cookies = SimpleCookie(environ.get("HTTP_COOKIE", ""))
        client = cookies.get("client_id")
        return UUID(client.value) if client else None

    @sio.event
    @metrics.timed("socket", "connect")
    async def connect(sid, environ):  # type: ignore
        broker = get_socket_broker()
        client_id = await _extract_client_id(environ)
        # Recusa conexão se não tiver client_id
        if not client_id:
            logger.warning("Conexão WS recusada: sem client_id")
            return False

        broker.register_client(client_id, sid)

        logger.debug("Cliente WS conectado: %s (sid=%s)", client_id, sid)
        return True

    @sio.event
    @metrics.timed("socket", "disconnect")
    async def disconnect(sid):  # type: ignore
        broker = get_socket_broker()
        client_id = broker.get_client_id_by_sid(sid)

        # O jogador sai da sala quando fecha a última aba: as outras seguem com ele dentro
        if client_id and broker.remove_client(client_id, sid):
            UserManager.unregister(client_id)
            logger.debug("Cliente WS desconectado: %s (sid=%s)", client_id, sid)

    @sio.event
    @metrics.timed("socket", "subscribe")
    async def subscribe(sid, data):  # type: ignore
        broker = get_socket_broker()
        client_id = broker.get_client_id_by_sid(sid)

        if not client_id:
            return

        events = data.get("events", [])
        broker.update_subscription(sid, events)

        await sio.emit("subscribed", {"events": events}, to=sid)
        logger.debug("Cliente WS inscrito: %s -> %s", client_id, events)
