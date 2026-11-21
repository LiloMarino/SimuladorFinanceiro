from abc import ABC, abstractmethod
from collections.abc import Iterable

from backend.types import SID, ClientID, Event, JSONValue


class RealtimeBroker(ABC):
    """
    Interface base para um broker de comunicação *realtime*.
    Implementa o padrão Publish/Subscribe (Pub/Sub) de forma simplificada.

    Um RealtimeBroker gerencia:
      - Subscribers (clientes WebSocket conectados)
      - Publicações de eventos (via notify)
    """

    @abstractmethod
    def update_subscription(self, sid: SID, events: Iterable[Event]) -> None:
        """Atualiza os eventos de interesse de uma conexão."""
        raise NotImplementedError

    @abstractmethod
    def subscribed_clients(self, event: Event) -> set[ClientID]:
        """Os clientes com alguma conexão assinando o evento."""
        raise NotImplementedError

    @abstractmethod
    def remember_request(
        self, event: Event, client_id: ClientID, request: object
    ) -> None:
        """Guarda o último pedido do cliente num evento de assinatura com parâmetro."""
        raise NotImplementedError

    @abstractmethod
    def requests(self, event: Event) -> dict[ClientID, object]:
        """Os pedidos guardados dos clientes que ainda assinam o evento."""
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
