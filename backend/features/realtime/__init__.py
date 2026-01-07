from flask import current_app

from backend.features.realtime.realtime_broker import RealtimeBroker
from backend.features.realtime.sse_broker import SSEBroker
from backend.features.realtime.ws_broker import SocketBroker
from backend.types import ClientID, Event, JSONValue


def get_broker() -> RealtimeBroker:
    """
    Retorna o broker Singleton Pub/Sub ativo (SSE, WebSocket, etc.).
    Configurado na inicialização da app Flask.
    """
    broker = current_app.config.get("realtime_broker")
    if not broker:
        raise RuntimeError("RealtimeBroker não está inicializado")
    return broker


def get_socket_broker() -> SocketBroker:
    broker = get_broker()
    if not isinstance(broker, SocketBroker):
        raise TypeError("Broker não é SocketBroker")
    return broker


def get_sse_broker() -> SSEBroker:
    broker = get_broker()
    if not isinstance(broker, SSEBroker):
        raise TypeError("Broker não é SSEBroker")
    return broker


def notify(event: Event, payload: JSONValue, to: ClientID | None = None) -> None:
    """
    API pública para publicar eventos realtime (Pub/Sub).
    Pode ser chamada de qualquer parte do backend.

    Exemplo:
    ```python
        from backend.realtime import notify
        notify("trade_update", {"id": 1, "price": 100})
    ```
    """
    get_broker().notify(event, payload, to)
