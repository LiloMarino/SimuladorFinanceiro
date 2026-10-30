import logging
from http.cookies import SimpleCookie
from uuid import UUID

from socketio import AsyncServer

from backend.core.enum import PlayerActivity
from backend.core.metrics import metrics
from backend.core.runtime.user_manager import UserManager
from backend.features.candle_challenge.game import candle_game
from backend.features.realtime import get_socket_broker

logger = logging.getLogger(__name__)


def register_ws_handlers(sio: AsyncServer):
    async def _extract_client_id(environ) -> UUID | None:
        cookies = SimpleCookie(environ.get("HTTP_COOKIE", ""))
        client = cookies.get("client_id")
        if not client:
            logger.warning("Conexão WS recusada: sem client_id")
            return None
        try:
            return UUID(client.value)
        except ValueError:
            logger.warning("Conexão WS recusada: client_id inválido (%r)", client.value)
            return None

    @sio.event
    @metrics.timed("socket", "connect")
    async def connect(sid, environ):
        broker = get_socket_broker()
        client_id = await _extract_client_id(environ)
        if not client_id:
            return False

        broker.register_client(client_id, sid)

        logger.debug("Cliente WS conectado: %s (sid=%s)", client_id, sid)
        return True

    @sio.event
    @metrics.timed("socket", "disconnect")
    async def disconnect(sid):
        broker = get_socket_broker()
        client_id = broker.get_client_id_by_sid(sid)

        if not client_id:
            return

        # O jogador sai da sala quando fecha a última aba: as outras seguem com ele dentro,
        # e o selo passa a ser o dessas
        if broker.remove_client(client_id, sid):
            user = UserManager.get_user(client_id)
            UserManager.unregister(client_id)
            if user is not None:
                candle_game.leave(user.id)
            logger.debug("Cliente WS desconectado: %s (sid=%s)", client_id, sid)
        else:
            UserManager.drop_activity(client_id, sid)

    @sio.event
    @metrics.timed("socket", "subscribe")
    async def subscribe(sid, data):
        broker = get_socket_broker()
        client_id = broker.get_client_id_by_sid(sid)

        if not client_id:
            return

        events = data.get("events", [])
        broker.update_subscription(sid, events)

        await sio.emit("subscribed", {"events": events}, to=sid)
        logger.debug("Cliente WS inscrito: %s -> %s", client_id, events)

    @sio.event
    @metrics.timed("socket", "presence")
    async def presence(sid, data):
        client_id = get_socket_broker().get_client_id_by_sid(sid)
        if not client_id or not isinstance(data, dict):
            return

        # `activity` nulo é "Online"; valor fora do catálogo não vira selo
        raw = data.get("activity")
        try:
            activity = None if raw is None else PlayerActivity(raw)
        except ValueError:
            logger.debug("Atividade desconhecida de %s: %r", client_id, raw)
            return

        UserManager.set_activity(client_id, sid, activity)
