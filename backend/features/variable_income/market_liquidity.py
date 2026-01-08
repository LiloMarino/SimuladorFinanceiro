from __future__ import annotations

from backend.features.variable_income.entities.candle import Candle
from backend.features.variable_income.entities.order import LimitOrder, OrderAction
from backend.features.variable_income.liquidity.beta_distribution import (
    BetaLiquidityDistribution,
)
from backend.features.variable_income.liquidity.liquidity_distribution import (
    LiquidityDistribution,
)
from backend.features.variable_income.order_book import OrderBook


class MarketLiquidity:
    """
    Injeta liquidez sintética no OrderBook a partir de OHLCV.

    Conceito:
    - Typical Price define o centro (BUY vs SELL)
    - Beta Distribution define densidade de ordens
    - Candle define range e volume
    """

    MARKET_CLIENT_ID = "__MARKET__"

    def __init__(
        self,
        *,
        order_book: OrderBook,
        distribution: LiquidityDistribution | None = None,
    ):
        self.order_book = order_book
        self.distribution: LiquidityDistribution = (
            distribution or BetaLiquidityDistribution()
        )

        # Rastreia ordens do mercado por ticker
        self._market_orders: dict[str, list[str]] = {}

    # =========================
    # Public API
    # =========================

    def refresh(self, candle: Candle) -> None:
        """
        - Remove liquidez antiga
        - Gera nova liquidez baseada no candle
        - Injeta no OrderBook
        """
        self._remove_old_orders(candle.ticker)

        orders = self._generate_orders(candle)

        self._market_orders[candle.ticker] = []
        for order in orders:
            self.order_book.add(order)
            self._market_orders[candle.ticker].append(order.id)

    # =========================
    # Geração de liquidez
    # =========================

    def _generate_orders(self, candle: Candle) -> list[LimitOrder]:
        if candle.high <= candle.low or candle.volume <= 0:
            return []

        center = self._typical_price(candle)

        levels = self.distribution.generate(candle)

        orders: list[LimitOrder] = []

        for level in levels:
            if level.volume <= 0:
                continue

            if level.price < center:
                action = OrderAction.BUY
            elif level.price > center:
                action = OrderAction.SELL
            else:
                # Evita cruzamento artificial exatamente no centro
                continue

            orders.append(
                LimitOrder(
                    client_id=self.MARKET_CLIENT_ID,
                    ticker=candle.ticker,
                    price=level.price,
                    size=level.volume,
                    action=action,
                )
            )

        return orders

    # =========================
    # Helpers semânticos
    # =========================

    def _typical_price(self, candle: Candle) -> float:
        """
        Typical Price:
        (High + Low + Close) / 3

        Define o centro semântico do mercado.
        """
        return (candle.high + candle.low + candle.close) / 3

    # =========================
    # Lifecycle
    # =========================

    def _remove_old_orders(self, ticker: str) -> None:
        ids = self._market_orders.get(ticker, [])
        for order_id in ids:
            order = self.order_book.find(order_id)
            if order:
                self.order_book.remove(order)

        self._market_orders[ticker] = []
