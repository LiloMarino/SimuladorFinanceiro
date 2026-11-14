from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from backend.core.enum import OrderAction
from backend.core.exceptions import InsufficentPositionError


@dataclass
class FundAccount:
    """O que o motor move nos negócios da cota de uma gestora.

    `quotas` conta todas as cotas em circulação, inclusive as do formador. O formador
    negocia com um estoque e um caixa sintéticos, que moram aqui e não geram evento.
    """

    # A conta da gestora no motor, que recebe o dinheiro da oferta
    client_id: UUID
    quotas: Decimal
    maker_quotas: Decimal = Decimal(0)
    maker_cash: Decimal = Decimal(0)
    # Nulo sem oferta aberta
    offer_remaining: Decimal | None = None

    @property
    def outside_quotas(self) -> Decimal:
        """As cotas fora da mão do formador: a base das taxas."""
        return self.quotas - self.maker_quotas

    def subscribe_maker(self, size: Decimal, price: Decimal) -> None:
        """O formador subscreve cotas novas ao preço dado, pagando com o caixa sintético."""
        self.quotas += size
        self.maker_quotas += size
        self.maker_cash -= size * price

    def maker_trade(self, action: OrderAction, size: Decimal, price: Decimal) -> None:
        """Compra do formador sobe o estoque e gasta o caixa; a venda faz o inverso."""
        if action == OrderAction.BUY:
            self.maker_quotas += size
            self.maker_cash -= size * price
            return
        if size > self.maker_quotas:
            raise InsufficentPositionError()
        self.maker_quotas -= size
        self.maker_cash += size * price

    def issue(self, size: Decimal) -> None:
        """A oferta vendeu `size` cotas: elas passam a existir e saem do saldo da oferta."""
        if self.offer_remaining is None or size > self.offer_remaining:
            raise ValueError("Não há oferta aberta para emitir essa quantidade")
        self.quotas += size
        self.offer_remaining -= size
