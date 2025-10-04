# backend/realtime/ws_manager.py
import logging
from typing import Any, Optional

from flask_socketio import SocketIO

from .realtime_base import RealtimeManagerBase

logger = logging.getLogger(__name__)


class SocketManager(RealtimeManagerBase):
    """
    Adapter simples que usa flask_socketio.SocketIO para implementar o contrato.
    NOTE: para WebSocket o controle de clients (connect/disconnect) é manejado pelo socketio.
    """

    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        # Opcional: mapa de client metadata (sid -> meta)
        self._meta = {}

    def register_client(self, client_id: Optional[str] = None, **meta) -> str:
        # No socketio o client_id normalmente é o sid recebido em event connect.
        # Aqui apenas armazenamos meta se client_id for provisto.
        if client_id:
            self._meta[client_id] = meta
        return client_id or ""

    def remove_client(self, client_id: str) -> None:
        self._meta.pop(client_id, None)

    def update_subscription(self, client_id: str, topics):
        # Com socketio você pode usar rooms em vez de topics; aqui um placeholder.
        # Implementação de rooms requer chamadas socketio.join_room(...)
        logger.debug("SocketManager.update_subscription %s -> %s", client_id, topics)

    def broadcast(self, event: str, payload: Any, topic: Optional[str] = None) -> None:
        # topic semantics could be mapped to rooms (if used)
        if topic:
            # if you maintain implicit rooms, you can emit to a room: self.socketio.emit(event, payload, room=topic)
            self.socketio.emit(event, payload)
        else:
            self.socketio.emit(event, payload)

    def send_to(self, client_id: str, event: str, payload: Any) -> None:
        try:
            self.socketio.emit(event, payload, to=client_id)
        except Exception as e:
            logger.exception("Error sending to %s: %s", client_id, e)
