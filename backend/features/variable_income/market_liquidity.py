from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

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
        self._market_orders: dict[str, list[str]] = defaultdict(list)

    # =========================
    # Public API
    # =========================

    def refresh(
        self, candle: Candle, process_order: Callable[[LimitOrder], bool]
    ) -> None:
        """
        - Remove liquidez antiga
        - Gera nova liquidez baseada no candle
        - Injeta no OrderBook
        """
        self._remove_old_orders(candle.ticker)

        orders = self._generate_orders(candle)

        for order in orders:
            added = process_order(order)
            if added:
                self._market_orders[candle.ticker].append(order.id)

        return None

    # =========================
    # Geração de liquidez
    # =========================

    def _generate_orders(self, candle: Candle) -> list[LimitOrder]:
        if candle.high < candle.low or candle.volume <= 0:
            return []

        if candle.high == candle.low:
            return self._generate_flat_market(candle)

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

    def _generate_flat_market(self, candle: Candle) -> list[LimitOrder]:
        """
        Mercado com alto volume concentrado em um único preço.
        Criamos spread técnico mínimo para permitir matching.
        """
        price = candle.close
        tick = 0.01

        half_volume = candle.volume // 2

        if half_volume <= 0:
            return []

        return [
            LimitOrder(
                client_id=self.MARKET_CLIENT_ID,
                ticker=candle.ticker,
                price=price - tick,
                size=half_volume,
                action=OrderAction.BUY,
            ),
            LimitOrder(
                client_id=self.MARKET_CLIENT_ID,
                ticker=candle.ticker,
                price=price + tick,
                size=candle.volume - half_volume,
                action=OrderAction.SELL,
            ),
        ]

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
