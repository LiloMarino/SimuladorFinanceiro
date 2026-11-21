import asyncio
import json
import time
from collections import defaultdict
from collections.abc import Iterable
from threading import Lock

from socketio import AsyncServer

from backend.core.metrics import metrics
from backend.core.runtime.realtime_broker import RealtimeBroker
from backend.types import SID, ClientID, Event, JSONValue


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
        # Último pedido de cada cliente num evento de assinatura com parâmetro
        self._requests: dict[Event, dict[ClientID, object]] = defaultdict(dict)
        # Pedidos que chegaram antes de a aba assinar o evento
        self._awaiting: set[tuple[Event, ClientID]] = set()

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
            if sids is not None:
                sids.discard(sid)
            self._forget_unsubscribed_requests(client_id)
            if sids is None:
                return True

            if sids:
                return False

            del self._client_to_sids[client_id]
            return True

    def get_client_id_by_sid(self, sid: SID) -> ClientID | None:
        with self._lock:
            return self._sid_to_client.get(sid)

    def update_subscription(self, sid: SID, events: Iterable[Event]) -> None:
        """Troca os eventos que a conexão assina pela lista nova."""
        events = list(events)
        with self._lock:
            for subs in self._subscriptions.values():
                subs.discard(sid)
            for event in events:
                self._subscriptions[event].add(sid)
            client_id = self._sid_to_client.get(sid)
            if client_id is not None:
                self._awaiting -= {(event, client_id) for event in events}
                self._forget_unsubscribed_requests(client_id)

    def remember_request(self, event: Event, client_id: ClientID, request: object):
        """Guarda o último pedido do cliente no evento, para recalcular a cada publicação."""
        with self._lock:
            self._requests[event][client_id] = request
            sids = self._client_to_sids.get(client_id, set())
            if not (self._subscriptions.get(event, set()) & sids):
                self._awaiting.add((event, client_id))

    def requests(self, event: Event) -> dict[ClientID, object]:
        """Os pedidos guardados dos clientes que ainda assinam o evento."""
        with self._lock:
            subscribed = {
                self._sid_to_client[sid]
                for sid in self._subscriptions.get(event, set())
                if sid in self._sid_to_client
            }
            return {
                client_id: request
                for client_id, request in self._requests.get(event, {}).items()
                if client_id in subscribed
            }

    def _forget_unsubscribed_requests(self, client_id: ClientID) -> None:
        """
        O pedido vive enquanto o cliente assina o evento. Um pedido que chega antes do
        subscribe da aba fica guardado: só cai quando o cliente já assinou e deixou de assinar.
        """
        # Chamado com o lock tomado
        sids = self._client_to_sids.get(client_id, set())
        for event in list(self._requests):
            if client_id not in self._requests[event]:
                continue
            if sids and (event, client_id) in self._awaiting:
                continue
            if not (self._subscriptions.get(event, set()) & sids):
                del self._requests[event][client_id]
                self._awaiting.discard((event, client_id))

    def subscribed_clients(self, event: Event) -> set[ClientID]:
        with self._lock:
            return {
                self._sid_to_client[sid]
                for sid in self._subscriptions.get(event, set())
                if sid in self._sid_to_client
            }

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

        if not metrics.enabled:
            for sid in targets:
                asyncio.run_coroutine_threadsafe(
                    self.sio.emit(event, payload, to=sid),
                    self._loop,
                )
            return

        size = len(json.dumps(payload)) if targets else 0
        metrics.record_sent(event, len(targets), size)
        queued_at = time.perf_counter()
        for sid in targets:
            asyncio.run_coroutine_threadsafe(
                self._emit_measured(event, payload, sid, queued_at),
                self._loop,
            )

    async def _emit_measured(
        self, event: Event, payload: JSONValue, sid: SID, queued_at: float
    ) -> None:
        """O atraso conta a espera na fila do event loop e a entrega ao socket."""
        await self.sio.emit(event, payload, to=sid)
        metrics.record_queue(event, (time.perf_counter() - queued_at) * 1000)
