from threading import Lock
from typing import ClassVar

from backend.core import repository
from backend.core.dto.events.base_event import BaseEventDTO, PortfolioEventDTO


class EventManager:
    """
    Gerenciador singleton de eventos da aplicação.

    Responsável por:
    - Acumular eventos em memória de forma thread-safe
    - Persistir eventos em lote no banco de dados
    - Garantir que eventos não sejam perdidos durante concorrência
    """

    _events: ClassVar[list[BaseEventDTO]] = []
    # Carteiras com evento financeiro desde a última leitura; o flush não as esvazia
    _touched_portfolios: ClassVar[set[int]] = set()
    _lock = Lock()

    @classmethod
    def push_event(cls, event: BaseEventDTO) -> None:
        with cls._lock:
            cls._events.append(event)
            if isinstance(event, PortfolioEventDTO):
                cls._touched_portfolios.add(event.portfolio_id)

    @classmethod
    def pop_touched_portfolios(cls) -> set[int]:
        """As carteiras com evento financeiro desde a última chamada; zera a marcação."""
        with cls._lock:
            touched = set(cls._touched_portfolios)
            cls._touched_portfolios.clear()
            return touched

    @classmethod
    def flush(cls) -> None:
        with cls._lock:
            if not cls._events:
                return
            repository.event.insert_many(cls._events)
            cls._events.clear()
