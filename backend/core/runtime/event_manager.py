from threading import Lock
from typing import ClassVar

from backend.core import repository
from backend.core.dto.events.base_event import BaseEventDTO


class EventManager:
    """
    Gerenciador singleton de eventos da aplicação.

    Responsável por:
    - Acumular eventos em memória de forma thread-safe
    - Persistir eventos em lote no banco de dados
    - Garantir que eventos não sejam perdidos durante concorrência
    """

    _events: ClassVar[list[BaseEventDTO]] = []
    _lock = Lock()

    @classmethod
    def push_event(cls, event: BaseEventDTO) -> None:
        with cls._lock:
            cls._events.append(event)

    @classmethod
    def flush(cls) -> None:
        with cls._lock:
            if not cls._events:
                return
            repository.event.insert_many(cls._events)
            cls._events.clear()
