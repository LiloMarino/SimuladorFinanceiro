import json
import uuid
from collections.abc import Iterable
from queue import Empty, Queue
from threading import Lock

from flask import Response, request, stream_with_context

from backend.core.logger import setup_logger
from backend.types import JSONValue

from .realtime_broker import RealtimeBroker

logger = setup_logger(__name__)


class SSEBroker(RealtimeBroker):
    """
    Implementação do broker Pub/Sub usando Server-Sent Events (SSE).
    Cada cliente possui uma fila (Queue) e um conjunto de tópicos de interesse.
    Mantém clientes assinantes e envia mensagens via stream HTTP unidirecional.
    """

    def __init__(self):
        self._subscriptions: dict[str, set[str]] = {}  # event -> set(client_id)
        self._clients: dict[str, Queue] = {}  # client_id -> Queue
        self._lock = Lock()

    # --------------------------------------------------------------------- #
    # Subscription Management
    # --------------------------------------------------------------------- #
    def register_client(self, client_id: str | None = None) -> str:
        if client_id is None:
            client_id = str(uuid.uuid4())

        with self._lock:
            if client_id not in self._clients:
                self._clients[client_id] = Queue()

        logger.debug("SSEBroker.register_client %s", client_id)
        return client_id

    def remove_client(self, client_id: str) -> None:
        with self._lock:
            self._clients.pop(client_id, None)
            # Remove de todas as assinaturas
            for subscribers in self._subscriptions.values():
                subscribers.discard(client_id)

        logger.debug("SSEBroker.remove_client %s", client_id)

    def update_subscription(self, client_id: str, events: Iterable[str]) -> None:
        with self._lock:
            # Remove de todos os eventos atuais
            for subscribers in self._subscriptions.values():
                subscribers.discard(client_id)
            # Adiciona para os novos eventos
            for event in events:
                self._subscriptions.setdefault(event, set()).add(client_id)

        logger.debug("SSEBroker.update_subscription %s -> %s", client_id, events)

    # --------------------------------------------------------------------- #
    # Publish
    # --------------------------------------------------------------------- #
    def notify(self, event: str, payload: JSONValue) -> None:
        """Envia payload para todos os clientes inscritos neste evento."""
        packet = f"event: {event}\ndata: {json.dumps({'event': event, 'payload': payload})}\n\n"

        with self._lock:
            for cid in self._subscriptions.get(event, set()):
                q = self._clients.get(cid)
                if q:
                    try:
                        q.put(packet)
                    except Exception:
                        logger.exception("Erro ao enfileirar mensagem para %s", cid)

    # --------------------------------------------------------------------- #
    # Connection handler
    # --------------------------------------------------------------------- #
    def connect(self):
        """Rota SSE: cria client e retorna Response que streama eventos."""
        client_id = request.args.get("client_id")

        client_id = self.register_client(client_id)
        self.update_subscription(client_id, [])
        logger.info("Cliente conectado: %s", client_id)
        return Response(
            stream_with_context(self._listen_generator(client_id)),
            mimetype="text/event-stream",
        )

    def _listen_generator(self, client_id: str):
        with self._lock:
            q = self._clients.get(client_id)
            if not q:
                return

        yield f"event: connected\ndata: {json.dumps({'client_id': client_id})}\n\n"

        try:
            while True:
                try:
                    packet = q.get(timeout=15)
                    yield packet
                except Empty:
                    continue
        except GeneratorExit:
            self.remove_client(client_id)
            logger.debug("SSEBroker: cliente desconectado %s", client_id)
