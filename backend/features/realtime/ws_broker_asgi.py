from collections import defaultdict
from collections.abc import Iterable
from threading import Lock

import socketio

from backend.core.logger import setup_logger
from backend.types import SID, ClientID, Event, JSONValue

from .realtime_broker import RealtimeBroker

logger = setup_logger(__name__)


class SocketBrokerASGI(RealtimeBroker):
    """
    Implementação do broker Pub/Sub usando python-socketio ASGI.
    Permite notificar clientes conectados via WebSocket.
    """

    def __init__(self, sio: socketio.AsyncServer):
        self.socketio = sio
        self._lock = Lock()
        self._subscriptions: dict[Event, set[ClientID]] = defaultdict(
            set
        )  # event -> set(client_id)
        self._client_to_sids: dict[ClientID, set[SID]] = defaultdict(
            set
        )  # client_id -> sids

    def register_client(self, client_id: ClientID, sid: SID) -> None:
        with self._lock:
            self._client_to_sids[client_id].add(sid)

    def remove_client(self, client_id: ClientID, sid: SID) -> None:
        with self._lock:
            sids = self._client_to_sids.get(client_id)
            if sids:
                sids.discard(sid)
                if not sids:
                    del self._client_to_sids[client_id]

            for subscribers in self._subscriptions.values():
                subscribers.discard(client_id)

    def update_subscription(self, client_id: ClientID, events: Iterable[Event]) -> None:
        with self._lock:
            for subscribers in self._subscriptions.values():
                subscribers.discard(client_id)
            for event in events:
                self._subscriptions[event].add(client_id)

    def notify(
        self,
        event: Event,
        payload: JSONValue,
        to: ClientID | None = None,
    ) -> None:
        """
        Note: This is synchronous but will be called from sync context.
        The actual emission is async and handled by socketio.
        """
        with self._lock:
            subscribers = self._subscriptions.get(event, set())
            if to is not None:
                if to not in subscribers:
                    return
                target_clients = {to}
            else:
                target_clients = subscribers

            for client_id in target_clients:
                sids = self._client_to_sids.get(client_id, set())
                for sid in sids:
                    # Note: emit is async but can be called from sync context
                    # socketio handles this internally
                    try:
                        import asyncio
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.create_task(self.socketio.emit(event, payload, to=sid))
                        else:
                            loop.run_until_complete(self.socketio.emit(event, payload, to=sid))
                    except RuntimeError:
                        # No event loop, use background task
                        import threading
                        threading.Thread(
                            target=lambda: asyncio.run(self.socketio.emit(event, payload, to=sid))
                        ).start()
