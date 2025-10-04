import json
import threading
from queue import Queue
from typing import Any, Dict, List

from flask import Response


class SSEManager:
    def __init__(self):
        self._clients: Dict[str, Queue] = {}
        self._lock = threading.Lock()

    def connect(self, client_id: str) -> Response:
        """Cria uma conexão SSE e registra o cliente."""
        q = Queue()
        with self._lock:
            self._clients[client_id] = q

        def stream():
            yield "event: connected\ndata: ok\n\n"
            try:
                while True:
                    data = q.get()
                    yield f"event: {data['event']}\ndata: {json.dumps(data['payload'])}\n\n"
            except GeneratorExit:
                self.disconnect(client_id)

        return Response(stream(), mimetype="text/event-stream")

    def disconnect(self, client_id: str):
        """Remove o cliente desconectado."""
        with self._lock:
            self._clients.pop(client_id, None)

    def broadcast(self, event: str, payload: Any):
        """Envia o evento para todos os clientes conectados."""
        with self._lock:
            for q in self._clients.values():
                q.put({"event": event, "payload": payload})

    def send_to(self, client_id: str, event: str, payload: Any):
        """Envia o evento apenas para um cliente específico."""
        with self._lock:
            if client_id in self._clients:
                self._clients[client_id].put({"event": event, "payload": payload})

    def active_clients(self) -> List[str]:
        """Retorna a lista de clientes conectados."""
        return list(self._clients.keys())
