from __future__ import annotations

from datetime import date

import pytest

from backend.features.variable_income.entities.candle import Candle
from backend.features.variable_income.entities.order import LimitOrder, OrderAction
from backend.features.variable_income.liquidity.beta_distribution import (
    BetaLiquidityDistribution,
)
from backend.features.variable_income.market_liquidity import MarketLiquidity
from backend.features.variable_income.order_book import OrderBook


def _candle(
    *,
    high: float = 10.6,
    low: float = 9.7,
    close: float = 10.2,
    volume: int = 10_000,
) -> Candle:
    return Candle(
        ticker="ABCD",
        price_date=date(2020, 1, 6),
        open=10.0,
        high=high,
        low=low,
        close=close,
        volume=volume,
    )


def _refresh(candle: Candle) -> tuple[OrderBook, list[LimitOrder]]:
    """Roda um refresh que joga toda ordem gerada direto no book."""
    book = OrderBook()
    generated: list[LimitOrder] = []

    def _rest(order: LimitOrder) -> bool:
        generated.append(order)
        book.add(order)
        return True

    MarketLiquidity(order_book=book).refresh(candle, _rest)
    return book, generated


@pytest.mark.parametrize(
    "candle",
    [_candle(high=9, low=10), _candle(volume=0)],
    ids=["high-below-low", "no-volume"],
)
def test_invalid_candle_generates_no_orders(candle: Candle):
    """Candle sem volume ou com máxima abaixo da mínima não gera liquidez."""
    _, generated = _refresh(candle)

    assert generated == []


def test_flat_candle_opens_one_tick_spread():
    """Candle sem variação vira uma compra e uma venda a um centavo do fechamento."""
    _, generated = _refresh(_candle(high=10, low=10, close=10, volume=101))

    buy, sell = generated
    assert (buy.action, buy.price, buy.size) == (OrderAction.BUY, 9.99, 50)
    assert (sell.action, sell.price, sell.size) == (OrderAction.SELL, 10.01, 51)


def test_buys_below_and_sells_above_typical_price():
    """Compras ficam abaixo do preço típico e vendas acima, dentro da faixa do candle."""
    candle = _candle()
    typical = (candle.high + candle.low + candle.close) / 3

    _, generated = _refresh(candle)

    assert generated
    assert all(candle.low <= o.price <= candle.high for o in generated)
    assert all(o.price < typical for o in generated if o.action == OrderAction.BUY)
    assert all(o.price > typical for o in generated if o.action == OrderAction.SELL)
    assert all(o.client_id == MarketLiquidity.MARKET_CLIENT_ID for o in generated)


def test_refresh_replaces_previous_liquidity():
    """Um novo candle tira do book a liquidez sintética do candle anterior."""
    book = OrderBook()
    liquidity = MarketLiquidity(order_book=book)

    def _rest(order: LimitOrder) -> bool:
        book.add(order)
        return True

    liquidity.refresh(_candle(), _rest)
    first = book.get_orders("ABCD")
    liquidity.refresh(_candle(high=20.6, low=19.7, close=20.2), _rest)

    assert all(book.find(o.id) is None for o in first)
    assert all(
        isinstance(o, LimitOrder) and o.price >= 19.7 for o in book.get_orders("ABCD")
    )


def test_beta_distribution_keeps_volume_and_range():
    """Distribuição Beta reparte todo o volume do candle em preços dentro da faixa."""
    candle = _candle(volume=12_345)

    levels = BetaLiquidityDistribution().generate(candle)

    assert sum(level.volume for level in levels) == candle.volume
    assert all(candle.low <= level.price <= candle.high for level in levels)


def test_beta_distribution_needs_two_levels():
    """Distribuição com menos de dois níveis de preço é inválida."""
    with pytest.raises(ValueError):
        BetaLiquidityDistribution(levels=1)
