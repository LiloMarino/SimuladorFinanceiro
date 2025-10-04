from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional


class RealtimeManagerBase(ABC):
    """
    Interface / base class para gerenciadores de realtime (SSE / WebSocket).
    Implementações concretas devem prover os métodos abaixo.
    """

    @abstractmethod
    def register_client(self, client_id: Optional[str] = None, **meta) -> str:
        """
        Registra um cliente. Retorna o client_id (gerado se None).
        Meta pode incluir: topics, route, user_id, etc.
        """
        raise NotImplementedError

    @abstractmethod
    def remove_client(self, client_id: str) -> None:
        """Remove a referência a um cliente (quando desconecta)."""
        raise NotImplementedError

    @abstractmethod
    def update_subscription(self, client_id: str, topics: Iterable[str]) -> None:
        """Atualiza os tópicos (interesses) do cliente."""
        raise NotImplementedError

    @abstractmethod
    def broadcast(self, event: str, payload: Any, topic: Optional[str] = None) -> None:
        """
        Envia um evento para clientes.
        - If topic is None: send to all.
        - Else: send only to clients subscribed to topic.
        """
        raise NotImplementedError

    @abstractmethod
    def send_to(self, client_id: str, event: str, payload: Any) -> None:
        """Envia um evento apenas para um cliente identificado."""
        raise NotImplementedError
