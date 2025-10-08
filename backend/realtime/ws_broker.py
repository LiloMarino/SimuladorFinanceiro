import logging
from typing import Any, Iterable, Optional

from flask_socketio import SocketIO

from .realtime_broker import RealtimeBroker

logger = logging.getLogger(__name__)


class SocketBroker(RealtimeBroker):
    """
    Implementação do broker Pub/Sub usando Flask-SocketIO.
    Permite notificar clientes conectados via WebSocket.
    """

    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self._meta = {}
        self._subscriptions = {}  # client_id -> set(events)

    def register_client(self, client_id: Optional[str] = None, **meta) -> str:
        if client_id:
            self._meta[client_id] = meta
        return client_id or ""

    def remove_client(self, client_id: str) -> None:
        self._meta.pop(client_id, None)
        self._subscriptions.pop(client_id, None)

    def update_subscription(self, client_id: str, events: Iterable[str]) -> None:
        self._subscriptions[client_id] = set(events)
        logger.debug("SocketBroker.update_subscription %s -> %s", client_id, events)

    def notify(self, event: str, payload: Any) -> None:
        """Publica um evento para todos os assinantes interessados."""
        logger.debug("SocketBroker.notify event=%s payload=%s", event, payload)
        for cid, subscribed in list(self._subscriptions.items()):
            if not subscribed or event in subscribed:
                try:
                    self.socketio.emit(event, payload, to=cid)
                except Exception as e:
                    logger.exception("Erro emitindo para %s: %s", cid, e)
