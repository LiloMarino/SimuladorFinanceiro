from abc import ABC, abstractmethod
from collections.abc import Iterable

from backend.types import JSONValue


class RealtimeBroker(ABC):
    """
    Interface base para um broker de comunicação *realtime*.
    Implementa o padrão Publish/Subscribe (Pub/Sub) de forma simplificada.

    Um RealtimeBroker gerencia:
      - Subscribers (clientes SSE/WS conectados)
      - Publicações de eventos (via notify)
    """

    @abstractmethod
    def register_client(self, client_id: str | None = None) -> str:
        """Registra um cliente (subscriber)."""
        raise NotImplementedError

    @abstractmethod
    def remove_client(self, client_id: str) -> None:
        """Remove um cliente (quando desconecta)."""
        raise NotImplementedError

    @abstractmethod
    def update_subscription(self, client_id: str, events: Iterable[str]) -> None:
        """Atualiza os eventos de interesse do cliente."""
        raise NotImplementedError

    @abstractmethod
    def notify(self, event: str, payload: JSONValue) -> None:
        """Publica um evento para todos os assinantes interessados."""
        raise NotImplementedError

    @abstractmethod
    def connect(self):
        """Retorna Response streaming SSE (só SSE)"""
        raise NotImplementedError
