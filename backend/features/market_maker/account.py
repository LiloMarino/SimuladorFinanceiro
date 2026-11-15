from dataclasses import dataclass, field
from decimal import Decimal

from backend.core.enum import OrderAction
from backend.core.exceptions import InsufficentPositionError

# A fatia dos papéis em circulação que um bot pode ter num ativo de preço sintético (posição e compras abertas)
BOT_QUOTA_LIMIT = Decimal("0.20")


@dataclass
class DayTrades:
    """Os negócios do papel num pregão: a vela do dia sai daqui."""

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
class MakerAccount:
    """O que o motor move nos negócios de um papel de preço sintético, ação ou cota.

    `quotas` conta todos os papéis em circulação, inclusive os do formador. O formador
    negocia com um estoque e um caixa sintéticos, que moram aqui e não geram evento.
    """

    quotas: Decimal
    maker_quotas: Decimal = Decimal(0)
    maker_cash: Decimal = Decimal(0)
    # Os negócios do pregão corrente; `take_day` fecha o pregão e zera
    day: DayTrades = field(default_factory=DayTrades)

    @property
    def outside_quotas(self) -> Decimal:
        """Os papéis fora da mão do formador: a base das taxas."""
        return self.quotas - self.maker_quotas

    def subscribe_maker(self, size: Decimal, price: Decimal) -> None:
        """O formador subscreve papéis novos ao preço dado, pagando com o caixa sintético."""
        self.quotas += size
        self.maker_quotas += size
        self.maker_cash -= size * price

    def receive_maker(self, size: Decimal) -> None:
        """O formador recebe papéis que já circulavam, sem pagar: o estoque dele sobe."""
        self.maker_quotas += size

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

    def record_trade(self, size: Decimal, price: Decimal) -> None:
        """Um negócio do papel entra nos números do pregão."""
        self.day.add(size, price)

    def take_day(self) -> DayTrades:
        """Entrega os negócios do pregão e abre o seguinte vazio."""
        day, self.day = self.day, DayTrades()
        return day
