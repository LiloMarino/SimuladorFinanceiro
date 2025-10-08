from typing import Any

from flask import current_app

from backend.realtime.realtime_broker import RealtimeBroker


def get_broker() -> RealtimeBroker:
    """
    Retorna o broker Singleton Pub/Sub ativo (SSE, WebSocket, etc.).
    Configurado na inicialização da app Flask.
    """
    broker = current_app.config.get("realtime_broker")
    if not broker:
        raise RuntimeError("Realtime broker not configured in current_app")
    return broker


def notify(event: str, payload: Any) -> None:
    """
    API pública para publicar eventos realtime (Pub/Sub).
    Pode ser chamada de qualquer parte do backend.

    Exemplo:
    ```python
        from backend.realtime import notify
        notify("trade_update", {"id": 1, "price": 100})
    ```
    """
    get_broker().notify(event, payload)
