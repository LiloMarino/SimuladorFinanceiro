from flask import request
from flask_socketio import SocketIO, emit

from backend.realtime import get_broker


def register_ws_handlers(socketio: SocketIO):
    @socketio.on("connect", namespace="/realtime")
    def on_connect():
        broker = get_broker()
        client_id: str = getattr(request, "sid")
        broker.register_client(client_id)
        print(f"WS client connected: {client_id}")

    @socketio.on("disconnect", namespace="/realtime")
    def on_disconnect():
        broker = get_broker()
        client_id: str = getattr(request, "sid")
        broker.remove_client(client_id)
        print(f"WS client disconnected: {client_id}")

    @socketio.on("subscribe", namespace="/realtime")
    def on_subscribe(data):
        broker = get_broker()
        client_id: str = getattr(request, "sid")
        topics = data.get("topics", [])
        broker.update_subscription(client_id, topics)
        emit("subscribed", {"topics": topics})
