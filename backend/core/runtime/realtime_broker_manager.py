from __future__ import annotations

from threading import Lock
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.features.realtime.realtime_broker import RealtimeBroker


class RealtimeBrokerManager:
    """
    Gerenciador singleton do broker de comunicação realtime.

    Responsável por:
    - Armazenar referência global ao RealtimeBroker configurado
    - Fornecer acesso thread-safe ao broker para toda a aplicação
    - Garantir que apenas um broker esteja ativo por vez
    """

    _lock = Lock()
    _broker: RealtimeBroker | None = None

    @classmethod
    def set_broker(cls, broker: RealtimeBroker) -> None:
        with cls._lock:
            cls._broker = broker

    @classmethod
    def get_broker(cls) -> RealtimeBroker:
        broker = cls._broker
        if not broker:
            raise RuntimeError("RealtimeBroker não está inicializado")
        return broker

    @classmethod
    def clear_broker(cls) -> None:
        with cls._lock:
            cls._broker = None
