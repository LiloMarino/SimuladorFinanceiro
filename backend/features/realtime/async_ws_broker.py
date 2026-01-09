"""
ASGI-compatible WebSocket broker using python-socketio.
This replaces the Flask-SocketIO implementation with a FastAPI-compatible one.
"""

from collections import defaultdict
from collections.abc import Iterable
from threading import Lock

import socketio

from backend.core.logger import setup_logger
from backend.types import SID, ClientID, Event, JSONValue

from .realtime_broker import RealtimeBroker

logger = setup_logger(__name__)


class AsyncSocketBroker(RealtimeBroker):
    """
    Implementação do broker Pub/Sub usando python-socketio com ASGI.
    Permite notificar clientes conectados via WebSocket compatível com FastAPI.
    """

    def __init__(self, sio: socketio.AsyncServer):
        self.sio = sio
        self._lock = Lock()
        self._subscriptions: dict[Event, set[ClientID]] = defaultdict(
            set
        )  # event -> set(client_id)
        self._client_to_sids: dict[ClientID, set[SID]] = defaultdict(
            set
        )  # client_id -> sids

    def register_client(self, client_id: ClientID, sid: SID) -> None:
        """Register a new client connection."""
        with self._lock:
            self._client_to_sids[client_id].add(sid)
            logger.info(f"Client registered: {client_id} (sid={sid})")

    def remove_client(self, client_id: ClientID, sid: SID) -> None:
        """Remove a client connection."""
        with self._lock:
            sids = self._client_to_sids.get(client_id)
            if sids:
                sids.discard(sid)
                if not sids:
                    del self._client_to_sids[client_id]

            for subscribers in self._subscriptions.values():
                subscribers.discard(client_id)
            logger.info(f"Client removed: {client_id} (sid={sid})")

    def update_subscription(self, client_id: ClientID, events: Iterable[Event]) -> None:
        """Update client's event subscriptions."""
        with self._lock:
            for subscribers in self._subscriptions.values():
                subscribers.discard(client_id)
            for event in events:
                self._subscriptions[event].add(client_id)
            logger.info(f"Subscription updated: {client_id} -> {list(events)}")

    def notify(
        self,
        event: Event,
        payload: JSONValue,
        to: ClientID | None = None,
    ) -> None:
        """
        Publish an event to subscribed clients.
        This method is synchronous and safe to call from sync code.
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
                    # Use background task to avoid blocking
                    try:
                        import asyncio

                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            task = asyncio.create_task(
                                self.sio.emit(event, payload, to=sid)
                            )
                            # Store task reference to avoid warning
                            task.add_done_callback(lambda t: None)
                        else:
                            # If no loop is running, schedule it
                            asyncio.run(self.sio.emit(event, payload, to=sid))
                    except RuntimeError:
                        # Fallback: use background task if async is not available
                        self.sio.start_background_task(
                            self.sio.emit, event, payload, to=sid
                        )
