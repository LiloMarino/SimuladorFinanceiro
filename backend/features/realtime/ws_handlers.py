from flask import request
from flask_socketio import SocketIO, emit

from backend.core.logger import setup_logger
from backend.features.realtime import get_socket_broker
from backend.features.users.user_manager import UserManager

logger = setup_logger(__name__)


def register_ws_handlers(socketio: SocketIO):
    @socketio.on("connect")
    def on_connect():  # type: ignore
        broker = get_socket_broker()
        client_id = request.cookies.get("client_id")
        sid = request.sid  # type: ignore[attr-defined]

        # Recusa conexão se não tiver client_id
        if not client_id:
            return False

        broker.register_client(client_id, sid)
        UserManager.register(client_id)
        logger.info(f"WS client connected: {client_id} (sid={sid})")

    @socketio.on("disconnect")
    def on_disconnect():  # type: ignore
        broker = get_socket_broker()
        client_id = request.cookies.get("client_id")
        sid = request.sid  # type: ignore[attr-defined]

        if client_id:
            broker.remove_client(client_id, sid)
            UserManager.unregister(client_id)
            logger.info(f"WS client disconnected: {client_id} (sid={sid})")

    @socketio.on("subscribe")
    def on_subscribe(data):  # type: ignore
        broker = get_socket_broker()
        client_id = request.cookies.get("client_id")

        if not client_id:
            return

        events = data.get("events", [])
        broker.update_subscription(client_id, events)
        emit("subscribed", {"events": events})
        logger.info(f"WS client subscribed: {client_id} -> {events}")
