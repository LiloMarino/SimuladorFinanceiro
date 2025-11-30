from flask import request
from flask_socketio import SocketIO, emit

from backend.core.logger import setup_logger
from backend.features.realtime import get_broker

logger = setup_logger(__name__)


def register_ws_handlers(socketio: SocketIO):
    @socketio.on("connect")
    def on_connect():  # type: ignore
        broker = get_broker()
        client_id: str = request.sid  # type: ignore[attr-defined]
        broker.register_client(client_id)
        logger.info(f"WS client connected: {client_id}")

    @socketio.on("disconnect")
    def on_disconnect():  # type: ignore
        broker = get_broker()
        client_id: str = request.sid  # type: ignore[attr-defined]
        broker.remove_client(client_id)
        logger.info(f"WS client disconnected: {client_id}")

    @socketio.on("subscribe")
    def on_subscribe(data):  # type: ignore
        broker = get_broker()
        client_id: str = request.sid  # type: ignore[attr-defined]
        events = data.get("events", [])  # Recebido do frontend
        broker.update_subscription(client_id, events)
        emit("subscribed", {"events": events})
