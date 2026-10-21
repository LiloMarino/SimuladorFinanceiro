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
    # Quem gerou evento desde a última leitura; o flush não o esvazia
    _touched_users: ClassVar[set[int]] = set()
    _lock = Lock()

    @classmethod
    def push_event(cls, event: BaseEventDTO) -> None:
        with cls._lock:
            cls._events.append(event)
            cls._touched_users.add(event.user_id)

    @classmethod
    def pop_touched_users(cls) -> set[int]:
        """Quem gerou evento desde a última chamada; zera a marcação."""
        with cls._lock:
            touched = set(cls._touched_users)
            cls._touched_users.clear()
            return touched

    @classmethod
    def flush(cls) -> None:
        with cls._lock:
            if not cls._events:
                return
            repository.event.insert_many(cls._events)
            cls._events.clear()
