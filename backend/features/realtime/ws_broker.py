import logging
from collections.abc import Iterable
from typing import Any

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
        self._clients = set()  # set de client_ids conectados
        self._subscriptions: dict[str, set[str]] = {}  # event -> set(client_id)

    def register_client(self, client_id: str | None = None) -> str:
        logger.info("Cliente conectado: %s", client_id)
        if client_id:
            self._clients.add(client_id)
        return client_id or ""

    def remove_client(self, client_id: str) -> None:
        self._clients.discard(client_id)
        for subscribers in self._subscriptions.values():
            subscribers.discard(client_id)
        logger.info("Cliente desconectado: %s", client_id)

    def update_subscription(self, client_id: str, events: Iterable[str]) -> None:
        logger.info("Atualizando assinaturas: %s -> %s", client_id, events)
        # Remove de todos os eventos atuais
        for subscribers in self._subscriptions.values():
            subscribers.discard(client_id)
        # Adiciona para os novos eventos
        for event in events:
            self._subscriptions.setdefault(event, set()).add(client_id)

    def notify(self, event: str, payload: Any) -> None:
        """Envia payload apenas para clientes inscritos neste evento."""
        for cid in self._subscriptions.get(event, set()):
            if cid in self._clients:
                try:
                    self.socketio.emit(event, payload, to=cid)
                except Exception as e:
                    logger.exception("Erro emitindo para %s: %s", cid, e)

    def connect(self) -> None:
        raise NotImplementedError("SocketBroker não implementa connect()")
