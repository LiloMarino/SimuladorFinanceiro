import math
from datetime import date
from decimal import Decimal

from backend.core.enum import OrderAction
from backend.features.funds.fund_account import FundAccount
from backend.features.variable_income.entities.order import (
    FUND_MAKER_CLIENT_ID,
    LimitOrder,
)
from backend.features.variable_income.matching_engine import MatchingEngine

# Distância da última ordem ao valor justo, em fração dele
BAND = 0.20
# Quantidade de cada lado, em fração das cotas em circulação
DEPTH = 0.02
LEVELS = 10
# Fração das cotas que o formador subscreve na oferta pública
STOCK_SHARE = 0.10

# Formato centro: o nível 1, o mais perto do valor justo, pesa mais; os pesos somam 1
_RAW_WEIGHTS = [1.05 - level / LEVELS for level in range(1, LEVELS + 1)]
WEIGHTS = [weight / sum(_RAW_WEIGHTS) for weight in _RAW_WEIGHTS]


class FundMaker:
    """Formador de mercado de uma cota: refaz todo dia a escada de ordens em volta do
    valor justo por cota.

    A venda sai do estoque do formador e a compra não tem limite. Cada nível entra pelo
    motor de casamento: o que cruza com uma ordem já no livro executa ao preço do próprio
    nível, sempre dentro da faixa, e o que sobra fica em repouso.
    """

    def __init__(
        self, engine: MatchingEngine, accounts: dict[str, FundAccount]
    ) -> None:
        self._engine = engine
        self._accounts = accounts
        self._orders: dict[str, list[LimitOrder]] = {}

    def refresh(
        self,
        ticker: str,
        fair_value: float,
        quotas_outstanding: Decimal,
        today: date,
    ) -> None:
        """Tira as ordens do formador e põe a escada nova, centrada em `fair_value`."""
        for order in self._orders.pop(ticker, []):
            self._engine.cancel(order_id=order.id, client_id=order.client_id)
        if fair_value <= 0:
            return
        account = self._accounts[ticker]
        side_quantity = float(quotas_outstanding) * DEPTH
        bids = self._ladder(ticker, fair_value, side_quantity, OrderAction.BUY, today)
        self._submit(ticker, bids)
        # A venda parte do estoque de depois das compras do dia
        stock = math.floor(account.maker_quotas)
        asks = self._ladder(
            ticker, fair_value, side_quantity, OrderAction.SELL, today, stock
        )
        self._submit(ticker, asks)

    def _ladder(
        self,
        ticker: str,
        fair_value: float,
        side_quantity: float,
        action: OrderAction,
        today: date,
        stock: int | None = None,
    ) -> list[LimitOrder]:
        sign = -1 if action == OrderAction.BUY else 1
        orders: list[LimitOrder] = []
        for level, weight in enumerate(WEIGHTS, start=1):
            quantity = math.floor(side_quantity * weight)
            if stock is not None:
                quantity = min(quantity, stock)
                stock -= quantity
            if quantity <= 0:
                continue
            orders.append(
                LimitOrder(
                    client_id=FUND_MAKER_CLIENT_ID,
                    ticker=ticker,
                    size=Decimal(quantity),
                    action=action,
                    placed_on=today,
                    price=round(fair_value * (1 + sign * BAND * level / LEVELS), 2),
                    fills_at_own_price=True,
                )
            )
        return orders

    def _submit(self, ticker: str, orders: list[LimitOrder]) -> None:
        """Casa cada nível com o livro e guarda o que repousa, para o refresh seguinte."""
        for order in orders:
            self._engine.submit(order)
            if order.remaining > 0:
                self._orders.setdefault(ticker, []).append(order)
