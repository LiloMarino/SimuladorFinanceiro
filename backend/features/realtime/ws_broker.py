import asyncio
import json
from collections import defaultdict
from collections.abc import Iterable
from threading import Lock

from socketio import AsyncServer

from backend.core.metrics import metrics
from backend.types import SID, ClientID, Event, JSONValue

from .realtime_broker import RealtimeBroker


class SocketBroker(RealtimeBroker):
    """
    Implementação Pub/Sub usando WebSocket (python-socketio).

    Responsável por:
    - Gerenciar conexões WebSocket bidirecionais com python-socketio
    - Mapear client_id para múltiplos SIDs (suporta múltiplas tabs)
    - Gerenciar assinaturas de eventos por cliente
    - Executar emissões de forma thread-safe via event loop
    - Suportar comunicação bidirecional (servidor → cliente e cliente → servidor)
    """

    def __init__(self, sio: AsyncServer):
        self.sio = sio
        self._lock = Lock()
        self._loop: asyncio.AbstractEventLoop | None = None
        # Cada aba assina os eventos da própria página: a assinatura é da conexão
        self._subscriptions: dict[Event, set[SID]] = defaultdict(set)  # event -> sids
        self._client_to_sids: dict[ClientID, set[SID]] = defaultdict(
            set
        )  # client_id -> sids
        self._sid_to_client: dict[SID, ClientID] = {}  # sid -> client_id

    def bind_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Associa o event loop principal para execuções thread-safe."""
        self._loop = loop

    def register_client(self, client_id: ClientID, sid: SID) -> None:
        """Registra um novo cliente WebSocket."""
        with self._lock:
            self._client_to_sids[client_id].add(sid)
            self._sid_to_client[sid] = client_id

    def remove_client(self, client_id: ClientID, sid: SID) -> bool:
        """Remove a conexão encerrada; True quando era a última aberta do cliente."""
        with self._lock:
            self._sid_to_client.pop(sid, None)
            for subs in self._subscriptions.values():
                subs.discard(sid)

            sids = self._client_to_sids.get(client_id)
            if sids is None:
                return True

            sids.discard(sid)
            if sids:
                return False

            del self._client_to_sids[client_id]
            return True

    def get_client_id_by_sid(self, sid: SID) -> ClientID | None:
        with self._lock:
            return self._sid_to_client.get(sid)

    def update_subscription(self, sid: SID, events: Iterable[Event]) -> None:
        """Troca os eventos que a conexão assina pela lista nova."""
        with self._lock:
            for subs in self._subscriptions.values():
                subs.discard(sid)
            for event in events:
                self._subscriptions[event].add(sid)

    def notify(
        self,
        event: Event,
        payload: JSONValue,
        to: ClientID | None = None,
    ) -> None:
        with self._lock:
            targets = set(self._subscriptions.get(event, set()))
            if to is not None:
                targets &= self._client_to_sids.get(to, set())

        if self._loop is None:
            raise RuntimeError("Event loop não está vinculado ao SocketBroker")

        if metrics.enabled:
            metrics.record_sent(event, len(targets), len(json.dumps(payload)))

        for sid in targets:
            asyncio.run_coroutine_threadsafe(
                self.sio.emit(event, payload, to=sid),
                self._loop,
            )
