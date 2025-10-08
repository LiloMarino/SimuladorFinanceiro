import json
import logging
import uuid
from queue import Empty, Queue
from threading import Lock
from typing import Any, Dict, Iterable, Optional

from flask import Response, request, stream_with_context

from .realtime_broker import RealtimeBroker

logger = logging.getLogger(__name__)


class SSEBroker(RealtimeBroker):
    """
    Implementação do broker Pub/Sub usando Server-Sent Events (SSE).
    Cada cliente possui uma fila (Queue) e um conjunto de tópicos de interesse.
    Mantém clientes assinantes e envia mensagens via stream HTTP unidirecional.
    """

    def __init__(self):
        self._clients: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    # --------------------------------------------------------------------- #
    # Subscription Management
    # --------------------------------------------------------------------- #
    def register_client(self, client_id: Optional[str] = None, **meta) -> str:
        if client_id is None:
            client_id = str(uuid.uuid4())

        with self._lock:
            if client_id in self._clients:
                # Atualiza metadata sem recriar a fila existente
                self._clients[client_id]["meta"].update(meta)
            else:
                q = Queue()
                self._clients[client_id] = {
                    "queue": q,
                    "events": set(meta.get("events", [])),
                    "meta": meta,
                }

        logger.debug("SSEBroker.register_client %s meta=%s", client_id, meta)
        return client_id

    def remove_client(self, client_id: str) -> None:
        with self._lock:
            self._clients.pop(client_id, None)
        logger.debug("SSEBroker.remove_client %s", client_id)

    def update_subscription(self, client_id: str, events: Iterable[str]) -> None:
        with self._lock:
            if client_id in self._clients:
                self._clients[client_id]["events"] = set(events)
                logger.debug(
                    "SSEBroker.update_subscription %s -> %s", client_id, events
                )

    # --------------------------------------------------------------------- #
    # Publish
    # --------------------------------------------------------------------- #
    def notify(self, event: str, payload: Any) -> None:
        """Publica um evento para todos os clientes interessados."""
        message = {"event": event, "payload": payload}
        blob = json.dumps(message)
        packet = f"event: {event}\ndata: {blob}\n\n"

        with self._lock:
            for cid, info in list(self._clients.items()):
                events = info.get("events")
                if not events or event in events:
                    try:
                        info["queue"].put(packet)
                    except Exception as e:
                        logger.exception(
                            "Erro ao enfileirar mensagem para %s: %s", cid, e
                        )

    # --------------------------------------------------------------------- #
    # Connection handler (for Flask route)
    # --------------------------------------------------------------------- #
    def connect(self):
        """Cria um cliente SSE e retorna um Response que streama os eventos."""
        client_id = request.args.get("client_id")
        events = request.args.getlist("event")
        meta = {}

        client_id = self.register_client(client_id=client_id, events=events, meta=meta)
        return Response(
            stream_with_context(self._listen_generator(client_id)),
            mimetype="text/event-stream",
        )

    def _listen_generator(self, client_id: str):
        """Generator que entrega pacotes do Queue ao cliente conectado."""
        with self._lock:
            info = self._clients.get(client_id)
            if not info:
                return
            q = info["queue"]

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

    # --------------------------------------------------------------------- #
    # Utilities
    # --------------------------------------------------------------------- #
    def get_active_clients(self):
        with self._lock:
            return list(self._clients.keys())
