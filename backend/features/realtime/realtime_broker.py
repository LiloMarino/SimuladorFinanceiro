from abc import ABC, abstractmethod
from collections.abc import Iterable

from backend.types import ClientID, Event, JSONValue


class RealtimeBroker(ABC):
    """
    Interface base para um broker de comunicação *realtime*.
    Implementa o padrão Publish/Subscribe (Pub/Sub) de forma simplificada.

    Um RealtimeBroker gerencia:
      - Subscribers (clientes SSE/WS conectados)
      - Publicações de eventos (via notify)
    """

    @abstractmethod
    def update_subscription(self, client_id: ClientID, events: Iterable[Event]) -> None:
        """Atualiza os eventos de interesse do cliente."""
        raise NotImplementedError

    @abstractmethod
    def notify(
        self,
        event: Event,
        payload: JSONValue,
        to: ClientID | None = None,
    ) -> None:
        """Publica um evento para todos os assinantes interessados."""
        raise NotImplementedError
