import json
import logging
import uuid
from queue import Empty, Queue
from threading import Lock
from typing import Any, Dict, Iterable, Optional

from flask import Response, request, stream_with_context

from .realtime_base import RealtimeManagerBase

logger = logging.getLogger(__name__)


class SSEManager(RealtimeManagerBase):
    """
    Gerenciador SSE:
    - Mantém clients: dict[client_id] -> {"queue": Queue(), "topics": set(), "meta": {...}}
    - connect() retorna um Response que streama eventos (usado na rota /api/stream)
    """

    def __init__(self):
        self._clients: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    def register_client(self, client_id: Optional[str] = None, **meta) -> str:
        if client_id is None:
            client_id = str(uuid.uuid4())
        with self._lock:
            if client_id in self._clients:
                # já existe: atualiza meta sem perder queue
                self._clients[client_id]["meta"].update(meta)
            else:
                q = Queue()
                self._clients[client_id] = {
                    "queue": q,
                    "topics": set(meta.get("topics", [])),
                    "meta": meta,
                }
        logger.debug("SSE register_client %s meta=%s", client_id, meta)
        return client_id

    def remove_client(self, client_id: str) -> None:
        with self._lock:
            self._clients.pop(client_id, None)
        logger.debug("SSE remove_client %s", client_id)

    def update_subscription(self, client_id: str, topics: Iterable[str]) -> None:
        with self._lock:
            if client_id in self._clients:
                self._clients[client_id]["topics"] = set(topics)
                logger.debug("SSE update_subscription %s -> %s", client_id, topics)

    def broadcast(self, event: str, payload: Any, topic: Optional[str] = None) -> None:
        """
        Se topic is None -> envia para todos
        Senão envia apenas para clientes com topic presente.
        """
        message = {"event": event, "payload": payload}
        blob = json.dumps(message)
        packet = f"event: {event}\ndata: {blob}\n\n"
        with self._lock:
            for cid, info in list(self._clients.items()):
                if topic is None or (info.get("topics") and topic in info["topics"]):
                    try:
                        info["queue"].put(packet)
                    except Exception as e:
                        logger.exception(
                            "Erro ao enfileirar mensagem para %s: %s", cid, e
                        )

    def send_to(self, client_id: str, event: str, payload: Any) -> None:
        packet = f"event: {event}\ndata: {json.dumps({'event': event, 'payload': payload})}\n\n"
        with self._lock:
            info = self._clients.get(client_id)
            if info:
                info["queue"].put(packet)

    def _listen_generator(self, client_id: str):
        """
        Generator que bloqueia em queue.get() e yield mensagens ao client.
        Chamado internamente pela rota /api/stream.
        """
        q = None
        with self._lock:
            info = self._clients.get(client_id)
            if not info:
                return
            q = info["queue"]

        # envia um evento inicial 'connected' com o client_id e meta
        meta = info.get("meta", {})
        initial = {
            "event": "connected",
            "payload": {"client_id": client_id, "meta": meta},
        }
        yield f"event: connected\ndata: {json.dumps(initial['payload'])}\n\n"

        try:
            while True:
                try:
                    packet = q.get(
                        timeout=15
                    )  # timeout para permitir checagens periódicas
                    yield packet
                except Empty:
                    # Heartbeat opcional (pode enviar comentário/keepalive)
                    # yield ": keepalive\n\n"
                    continue
        except GeneratorExit:
            # Cliente fechou a conexão
            self.remove_client(client_id)
            logger.debug("GeneratorExit - removed client %s", client_id)
            return

    # Helper para rota Flask
    def connect(self):
        """
        Rota deve chamar SSEManager.connect() para criar client e retornar Response.
        Aceita query params opcionais (ex: client_id, topics).
        """
        # Leitura de query params
        client_id = request.args.get("client_id")  # optional: client may pass stored id
        topics = request.args.getlist("topic")  # ?topic=X&topic=Y
        meta = {}
        # criar/registrar client
        client_id = self.register_client(client_id=client_id, topics=topics, meta=meta)
        # retornar Response com generator
        return Response(
            stream_with_context(self._listen_generator(client_id)),
            mimetype="text/event-stream",
        )

    # API utilitária para rotas REST
    def get_active_clients(self):
        with self._lock:
            return list(self._clients.keys())
