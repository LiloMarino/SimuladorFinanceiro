from backend.features.realtime.realtime_broker import RealtimeBroker
from backend.features.realtime.sse_broker import SSEBroker
from backend.features.realtime.ws_broker_asgi import SocketBrokerASGI
from backend.types import ClientID, Event, JSONValue


def get_broker() -> RealtimeBroker:
    """
    Retorna o broker Singleton Pub/Sub ativo (SSE, WebSocket, etc.).
    Configurado na inicialização da app FastAPI.
    """
    from main_fastapi import get_broker as get_fastapi_broker

    return get_fastapi_broker()


def get_socket_broker() -> SocketBrokerASGI:
    """Get the socket broker (FastAPI ASGI version)."""
    broker = get_broker()
    if not isinstance(broker, SocketBrokerASGI):
        raise TypeError("Broker não é SocketBrokerASGI")
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
