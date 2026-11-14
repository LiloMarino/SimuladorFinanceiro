from datetime import date

from backend.core.enum import OrderAction
from backend.features.funds.fund_account import FundAccount
from backend.features.variable_income.entities.order import (
    FUND_ISSUER_CLIENT_ID,
    LimitOrder,
)
from backend.features.variable_income.matching_engine import MatchingEngine


class FundOffer:
    """A oferta pública das cotas: uma ordem de venda da gestora, ao valor justo do dia,
    pelo que ainda falta vender (`offer_remaining`).

    A ordem casa com o que já está no livro ao valor justo, mesmo contra uma compra a
    preço maior, e o que sobra repousa."""

    def __init__(
        self, engine: MatchingEngine, accounts: dict[str, FundAccount]
    ) -> None:
        self._engine = engine
        self._accounts = accounts
        self._orders: dict[str, LimitOrder] = {}

    def refresh(self, ticker: str, fair_value: float, today: date) -> None:
        """Refaz a ordem da oferta ao valor justo; sem saldo a vender, o livro fica sem ela."""
        self._cancel(ticker)
        remaining = self._accounts[ticker].offer_remaining
        if not remaining or remaining <= 0:
            return
        order = LimitOrder(
            client_id=FUND_ISSUER_CLIENT_ID,
            ticker=ticker,
            size=remaining,
            action=OrderAction.SELL,
            placed_on=today,
            price=round(fair_value, 2),
            fills_at_own_price=True,
        )
        self._engine.submit(order)
        if order.remaining > 0:
            self._orders[ticker] = order

    def close(self, ticker: str) -> None:
        """Encerra a oferta: o que não vendeu não é emitido."""
        self._cancel(ticker)
        self._accounts[ticker].offer_remaining = None

    def _cancel(self, ticker: str) -> None:
        order = self._orders.pop(ticker, None)
        if order is not None:
            self._engine.cancel(order_id=order.id, client_id=order.client_id)
