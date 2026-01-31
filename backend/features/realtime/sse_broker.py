import json
from collections import defaultdict
from collections.abc import Iterable
from queue import Empty, Queue
from threading import Lock

from fastapi.responses import StreamingResponse

from backend.core.logger import setup_logger
from backend.core.runtime.user_manager import UserManager
from backend.types import ClientID, Event, JSONValue

from .realtime_broker import RealtimeBroker

logger = setup_logger(__name__)


class SSEBroker(RealtimeBroker):
    """
    Implementação Pub/Sub usando Server-Sent Events (SSE).

    Responsável por:
    - Manter filas (Queue) individuais para cada cliente conectado
    - Gerenciar assinaturas de eventos por cliente
    - Enviar mensagens via stream HTTP unidirecional
    - Registrar/remover clientes no UserManager
    - Fornecer StreamingResponse para FastAPI
    """

    def __init__(self):
        self._subscriptions: dict[Event, set[ClientID]] = defaultdict(
            set
        )  # event -> set(client_id)
        self._clients: dict[ClientID, Queue[str]] = {}  # client_id -> Queue
        self._lock = Lock()

    def register_client(self, client_id: ClientID) -> None:
        with self._lock:
            self._clients.setdefault(client_id, Queue())
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

    def notify(
        self,
        event: Event,
        payload: JSONValue,
        to: ClientID | None = None,
    ) -> None:
        """Envia payload para todos os clientes inscritos (thread-safe)."""
        packet = (
            f"event: {event}\n"
            f"data: {json.dumps({'event': event, 'payload': payload})}\n\n"
        )

        with self._lock:
            subscribers = self._subscriptions.get(event, set()).copy()
            if to is not None:
                target_clients = {to} if to in subscribers else set()
            else:
                target_clients = subscribers

        for cid in target_clients:
            q = self._clients.get(cid)
            if q:
                q.put(packet)

    # --------------------------------------------------------------------- #
    # Connection handler
    # --------------------------------------------------------------------- #
    def connect(self, client_id: str) -> StreamingResponse:
        """Rota SSE: cria client e retorna Response que streama eventos."""
        self.register_client(client_id)

        return StreamingResponse(
            self._listen_generator(client_id),
            media_type="text/event-stream",
        )

    def _listen_generator(self, client_id: str):
        """Generator que yields eventos SSE para o cliente."""
        with self._lock:
            q = self._clients.get(client_id)
            if not q:
                return

        # Mensagem inicial
        yield f"event: connected\ndata: {json.dumps({'client_id': client_id})}\n\n"

        try:
            while True:
                try:
                    yield q.get(timeout=15)
                except Empty:
                    yield ": heartbeat\n\n"
        finally:
            self.remove_client(client_id)
