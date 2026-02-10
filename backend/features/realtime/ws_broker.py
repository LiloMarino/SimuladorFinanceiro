import asyncio
import logging
from collections import defaultdict
from collections.abc import Iterable
from threading import Lock

from socketio import AsyncServer

from backend.types import SID, ClientID, Event, JSONValue

from .realtime_broker import RealtimeBroker

logger = logging.getLogger(__name__)


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
        self._subscriptions: dict[Event, set[ClientID]] = defaultdict(
            set
        )  # event -> set(client_id)
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

    def remove_client(self, client_id: ClientID, sid: SID) -> None:
        """Remove um cliente desconectado."""
        with self._lock:
            self._sid_to_client.pop(sid, None)

            sids = self._client_to_sids.get(client_id)
            if not sids:
                return

            sids.discard(sid)

            if not sids:
                del self._client_to_sids[client_id]
                for subs in self._subscriptions.values():
                    subs.discard(client_id)

    def get_client_id_by_sid(self, sid: SID) -> ClientID | None:
        with self._lock:
            return self._sid_to_client.get(sid)

    def update_subscription(self, client_id: ClientID, events: Iterable[Event]) -> None:
        """Atualiza os eventos que o cliente está inscrito."""
        with self._lock:
            for subs in self._subscriptions.values():
                subs.discard(client_id)
            for event in events:
                self._subscriptions[event].add(client_id)

    def notify(
        self,
        event: Event,
        payload: JSONValue,
        to: ClientID | None = None,
    ) -> None:
        with self._lock:
            subscribers = self._subscriptions.get(event, set()).copy()
            if to is not None:
                target_clients = {to} if to in subscribers else set()
            else:
                target_clients = subscribers

            targets = {
                sid
                for cid in target_clients
                for sid in self._client_to_sids.get(cid, set())
            }

        if self._loop is None:
            raise RuntimeError("Event loop não está vinculado ao SocketBroker")

        for sid in targets:
            asyncio.run_coroutine_threadsafe(
                self.sio.emit(event, payload, to=sid),
                self._loop,
            )
