from __future__ import annotations

from backend.features.variable_income.entities.candle import Candle
from backend.features.variable_income.entities.order import LimitOrder, OrderAction
from backend.features.variable_income.liquidity.beta_distribution import (
    BetaLiquidityDistribution,
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
        levels: int = 30,
        tick_size: float = 0.01,
        alpha: float = 4.0,
        beta: float = 4.0,
    ):
        self.order_book = order_book

        self.distribution = BetaLiquidityDistribution(
            levels=levels,
            tick_size=tick_size,
            alpha=alpha,
            beta=beta,
        )

        # rastreia ordens do mercado por ticker
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

        levels = self.distribution.generate(
            low=candle.low,
            high=candle.high,
        )

        orders: list[LimitOrder] = []
        half_volume = candle.volume // 2

        for level in levels:
            size = int(half_volume * level.weight)
            if size <= 0:
                continue

            if level.price < center:
                action = OrderAction.BUY
            elif level.price > center:
                action = OrderAction.SELL
            else:
                continue  # evita cruzamento no centro

            orders.append(
                LimitOrder(
                    client_id=self.MARKET_CLIENT_ID,
                    ticker=candle.ticker,
                    size=size,
                    action=action,
                    price=level.price,
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
