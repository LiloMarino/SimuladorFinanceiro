from flask import request
from flask_socketio import SocketIO, emit

from backend.features.realtime import get_broker
from backend.shared.utils.logger import setup_logger

logger = setup_logger(__name__)


def register_ws_handlers(socketio: SocketIO):
    @socketio.on("connect")
    def on_connect():
        broker = get_broker()
        client_id: str = getattr(request, "sid")
        broker.register_client(client_id)
        logger.info(f"WS client connected: {client_id}")

    @socketio.on("disconnect")
    def on_disconnect():
        broker = get_broker()
        client_id: str = getattr(request, "sid")
        broker.remove_client(client_id)
        logger.info(f"WS client disconnected: {client_id}")

    @socketio.on("subscribe")
    def on_subscribe(data):
        broker = get_broker()
        client_id: str = getattr(request, "sid")
        events = data.get("events", [])  # Recebido do frontend
        broker.update_subscription(client_id, events)
        emit("subscribed", {"events": events})
