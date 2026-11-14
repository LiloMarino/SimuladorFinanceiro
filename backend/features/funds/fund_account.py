from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

from backend.core.enum import OrderAction
from backend.core.exceptions import InsufficentPositionError

# A fatia das cotas em circulação que um bot pode ter numa gestora (posição e compras abertas)
BOT_QUOTA_LIMIT = Decimal("0.20")


@dataclass
class DayTrades:
    """Os negócios da cota num pregão: a vela do dia sai daqui."""

    open: Decimal | None = None
    high: Decimal = Decimal(0)
    low: Decimal = Decimal(0)
    close: Decimal = Decimal(0)
    quantity: Decimal = Decimal(0)
    value: Decimal = Decimal(0)

    def add(self, size: Decimal, price: Decimal) -> None:
        if self.open is None:
            self.open = self.high = self.low = price
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price
        self.quantity += size
        self.value += size * price


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
    # Os negócios do pregão corrente; `take_day` fecha o pregão e zera
    day: DayTrades = field(default_factory=DayTrades)

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
        """A oferta vendeu `size` cotas: elas passam a existir e saem do saldo da oferta.

        Sem saldo a vender a oferta está encerrada: `offer_remaining` volta a ser nulo.
        """
        if self.offer_remaining is None or size > self.offer_remaining:
            raise ValueError("Não há oferta aberta para emitir essa quantidade")
        self.quotas += size
        self.offer_remaining -= size
        if self.offer_remaining <= 0:
            self.offer_remaining = None

    def record_trade(self, size: Decimal, price: Decimal) -> None:
        """Um negócio da cota entra nos números do pregão."""
        self.day.add(size, price)

    def take_day(self) -> DayTrades:
        """Entrega os negócios do pregão e abre o seguinte vazio."""
        day, self.day = self.day, DayTrades()
        return day
