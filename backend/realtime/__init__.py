from flask import current_app

from backend.realtime.realtime_base import RealtimeManagerBase


def get_realtime_manager() -> RealtimeManagerBase:
    """Retorna o gerenciador de comunicação realtime atual (SSE ou WS)."""
    if "realtime_manager" not in current_app.config:
        raise RuntimeError("Realtime manager not configured")
    return current_app.config["realtime_manager"]
