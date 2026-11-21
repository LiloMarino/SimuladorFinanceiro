from backend.core.dto.base import BaseDTO
from backend.features.realtime import get_broker, notify, subscribed_clients
from backend.types import ClientID


class ClientRequests[R]:
    """
    Assinatura com parâmetro: o dado do aviso deriva do pedido que o cliente fez por HTTP
    (a prévia de uma ordem, os indicadores com os parâmetros escolhidos). O servidor guarda o
    último pedido de cada cliente por ativo e, a cada publicação, recalcula para quem ainda
    assina o evento `{prefix}:{ticker}` e entrega só àquele cliente.
    """

    def __init__(self, prefix: str):
        self.prefix = prefix

    def event(self, ticker: str) -> str:
        return f"{self.prefix}:{ticker}"

    def remember(self, ticker: str, client_id: ClientID, request: R) -> None:
        get_broker().remember_request(self.event(ticker), client_id, request)

    def pending(self, ticker: str) -> dict[ClientID, R]:
        """Os pedidos dos clientes que assinam o ativo agora; vazio quando ninguém assina."""
        event = self.event(ticker)
        if not subscribed_clients(event):
            return {}
        return get_broker().requests(event)  # type: ignore[return-value]

    def send(self, ticker: str, client_id: ClientID, payload: BaseDTO) -> None:
        notify(self.event(ticker), payload.to_json(), to=client_id)
