import json
from collections import defaultdict
from collections.abc import Iterable
from queue import Empty, Queue
from threading import Lock

from flask import Response, request, stream_with_context

from backend.core.logger import setup_logger
from backend.features.users.user_manager import UserManager
from backend.types import ClientID, Event, JSONValue

from .realtime_broker import RealtimeBroker

logger = setup_logger(__name__)


class SSEBroker(RealtimeBroker):
    """
    Implementação do broker Pub/Sub usando Server-Sent Events (SSE).
    Cada cliente possui uma fila (Queue) e um conjunto de tópicos de interesse.
    Mantém clientes assinantes e envia mensagens via stream HTTP unidirecional.
    """

    def __init__(self):
        self._subscriptions: dict[str, set[str]] = defaultdict(
            set
        )  # event -> set(client_id)
        self._clients: dict[str, Queue] = {}  # client_id -> Queue
        self._lock = Lock()

    def register_client(self, client_id: ClientID) -> None:
        with self._lock:
            if client_id not in self._clients:
                self._clients[client_id] = Queue()
        UserManager.register(client_id)
        logger.info("SSE conectado: %s", client_id)

    def remove_client(self, client_id: ClientID) -> None:
        with self._lock:
            self._clients.pop(client_id, None)

            # Remove de todas as assinaturas
            for subscribers in self._subscriptions.values():
                subscribers.discard(client_id)
        UserManager.unregister(client_id)
        logger.info("SSE desconectado: %s", client_id)

    def update_subscription(self, client_id: ClientID, events: Iterable[Event]) -> None:
        with self._lock:
            # Remove de todos os eventos atuais
            for subscribers in self._subscriptions.values():
                subscribers.discard(client_id)

            # Adiciona para os novos eventos
            for event in events:
                self._subscriptions[event].add(client_id)

    def notify(self, event: Event, payload: JSONValue) -> None:
        """Envia payload para todos os clientes inscritos."""
        packet = (
            f"event: {event}\n"
            f"data: {json.dumps({'event': event, 'payload': payload})}\n\n"
        )

        with self._lock:
            target_clients = self._subscriptions.get(event, set()).copy()

        for cid in target_clients:
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
        client_id = request.cookies.get("client_id")
        if not client_id:
            return Response("Unauthorized", status=401)

        self.register_client(client_id)
        self.update_subscription(client_id, [])
        return Response(
            stream_with_context(self._listen_generator(client_id)),
            mimetype="text/event-stream",
        )

    def _listen_generator(self, client_id: str):
        with self._lock:
            q = self._clients.get(client_id)
            if not q:
                return

        # Mensagem inicial
        yield (f"event: connected\ndata: {json.dumps({'client_id': client_id})}\n\n")

        try:
            while True:
                try:
                    packet = q.get(timeout=15)
                    yield packet
                except Empty:
                    # Mantém conexão viva
                    continue
        except GeneratorExit:
            self.remove_client(client_id)
