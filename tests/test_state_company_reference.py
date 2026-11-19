"""Preço de referência da estatal fundada: o desvio em volta do valor justo, o retorno do PIB no valor justo e a vela do dia sem negócio."""

from __future__ import annotations

import math
from datetime import date, timedelta
from decimal import Decimal
from typing import cast

import pytest

from backend.core.dto.state_company import StateCompanyDTO
from backend.core.dto.stock import StockDTO
from backend.core.enum import (
    AssetClass,
    StateCompanyOrigin,
    StateCompanySize,
    StateCompanyStatus,
    StateLever,
)
from backend.core.repository.economic import IndicatorHistory
from backend.features.market_maker.account import DayTrades
from backend.features.market_maker.candle import close_candle
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.state_companies import fair_value, reference
from backend.features.state_companies.book import StateCompanyBook
from backend.features.state_companies.market import StateCompanyMarket

D = Decimal
START = date(2004, 6, 1)


def sessions(count: int) -> list[date]:
    return [START + timedelta(days=i) for i in range(count)]


def returns_of(values: list[float]) -> list[tuple[date, float]]:
    return list(zip(sessions(len(values)), values, strict=True))


def test_market_drop_moves_the_price_by_beta():
    # Bolsa em -2% num pregão, sem ruído: a ação cai 0,8 de 2%, ou seja, 1,6%
    path = reference.deviation_path(
        returns_of([math.log(0.98)]), 1, noise=reference.no_noise
    )
    assert path[0] == pytest.approx(0.8 * math.log(0.98))
    assert math.exp(path[0]) - 1 == pytest.approx(-0.0159, abs=1e-3)


def test_deviation_halves_after_half_life():
    # Um choque de 10% e depois a meia-vida inteira de bolsa parada: sobra a metade do desvio
    shock = math.log(1.10) / 0.8
    path = reference.deviation_path(
        returns_of([shock] + [0.0] * reference.HALF_LIFE_SESSIONS),
        1,
        noise=reference.no_noise,
    )
    assert path[0] == pytest.approx(math.log(1.10))
    assert path[-1] == pytest.approx(path[0] / 2)


def test_noise_is_seeded_by_company_and_day():
    day = date(2004, 7, 1)
    assert reference.seeded_noise(7, day) == reference.seeded_noise(7, day)
    assert reference.seeded_noise(7, day) != reference.seeded_noise(8, day)
    assert reference.seeded_noise(7, day) != reference.seeded_noise(
        7, day + timedelta(days=1)
    )


def test_path_continues_from_where_it_stopped():
    # Calcular de uma vez ou em duas partes dá o mesmo desvio: ao vivo e recarregado coincidem
    series = returns_of([0.01, -0.02, 0.005, 0.0, 0.03, -0.01])
    whole = reference.deviation_path(series, 5)
    first = reference.deviation_path(series[:3], 5)
    rest = reference.deviation_path(series[3:], 5, initial=first[-1])
    assert whole == first + rest


def test_log_return_without_a_valid_previous_level_is_zero():
    assert reference.log_return(0.0, 100.0) == 0.0
    assert reference.log_return(100.0, 110.0) == pytest.approx(math.log(1.1))


def test_gdp_growth_above_trend_raises_the_fair_value():
    base = fair_value.fair_value(D("1000"), 3, D("0.05"), 12)
    above = fair_value.fair_value(
        D("1000"), 3, D("0.05"), 12, growth_path=[D("0.02")] * 12
    )
    below = fair_value.fair_value(
        D("1000"), 3, D("0.05"), 12, growth_path=[D("-0.02")] * 12
    )
    # 2 pontos de crescimento acima da tendência somam cerca de 4 pontos ao valor do ano
    assert 1.03 < float(above / base) < 1.05
    assert below < base < above


def test_growth_on_trend_changes_nothing():
    base = fair_value.fair_value(D("1000"), 3, D("0.05"), 24)
    assert (
        fair_value.fair_value(D("1000"), 3, D("0.05"), 24, growth_path=[D(0)] * 24)
        == base
    )


def test_month_rate_floor_keeps_the_value_positive():
    value = fair_value.fair_value(D("1000"), 3, D("0.05"), 6, growth_path=[D("-5")] * 6)
    assert value > 0


def stock() -> StockDTO:
    return StockDTO(id=1, ticker="ESTA3", name="Estatal", asset_class=AssetClass.STOCK)


def test_idle_candle_opens_at_previous_close_and_closes_at_reference():
    candle = close_candle(
        stock(),
        START,
        DayTrades(),
        previous_close=10.0,
        reference=D("10.5"),
        idle_close=D("10.5"),
    )
    assert (candle.open, candle.close) == (10.0, 10.5)
    assert (candle.high, candle.low) == (10.5, 10.0)
    assert candle.volume == 0


def test_idle_candle_debuts_flat_at_the_reference():
    candle = close_candle(
        stock(),
        START,
        DayTrades(),
        previous_close=None,
        reference=D("10"),
        idle_close=D("10"),
    )
    assert candle.open == candle.close == candle.high == candle.low == 10.0


def test_idle_candle_with_a_fall_has_the_previous_close_as_high():
    candle = close_candle(
        stock(),
        START,
        DayTrades(),
        previous_close=10.0,
        reference=D("9.4"),
        idle_close=D("9.4"),
    )
    assert (candle.high, candle.low) == (10.0, 9.4)


def test_candle_without_idle_close_repeats_the_previous_close():
    candle = close_candle(
        stock(), START, DayTrades(), previous_close=10.0, reference=D("12")
    )
    assert candle.open == candle.close == 10.0


def test_candle_with_trades_ignores_the_idle_close():
    trades = DayTrades()
    trades.add(D(5), D("10.2"))
    trades.add(D(5), D("10.4"))
    candle = close_candle(
        stock(),
        START,
        trades,
        previous_close=10.0,
        reference=D("11"),
        idle_close=D("11"),
    )
    assert (candle.open, candle.close) == (10.2, 10.4)


def founded_company() -> StateCompanyDTO:
    return StateCompanyDTO(
        id=1,
        stock_id=1,
        ticker="ESTA3",
        origin=StateCompanyOrigin.FOUNDED,
        government_share=D("0.5"),
        shares=1000,
        lever=StateLever.FUEL,
        size=StateCompanySize.MEDIUM,
        invested=D(1000),
        mean_return=D("0.05"),
        seed=11,
        status=StateCompanyStatus.ACTIVE,
        founded_on=START,
        offer_opened_on=None,
        privatized_on=None,
        proceeds=None,
    )


def market_over(
    monkeypatch: pytest.MonkeyPatch, levels: list[float], noise: reference.Noise
) -> StateCompanyMarket:
    """O pregão sobre um Ibovespa de `levels`, um nível por dia a partir de `START`."""
    days = sessions(len(levels))
    history = IndicatorHistory(
        days, {d: D(str(v)) for d, v in zip(days, levels, strict=True)}
    )
    monkeypatch.setattr(
        "backend.features.state_companies.market.repository.economic.get_history",
        lambda *_: history,
    )
    book = StateCompanyBook(1, 7, lambda: {}, [])
    return StateCompanyMarket(1, cast(SimulationEngine, None), book, noise)


def test_deviation_is_zero_on_the_founding_day(monkeypatch: pytest.MonkeyPatch):
    market = market_over(monkeypatch, [100.0, 98.0], reference.no_noise)
    assert market.deviation(founded_company(), START) == 0.0


def test_deviation_follows_the_market_index(monkeypatch: pytest.MonkeyPatch):
    market = market_over(monkeypatch, [100.0, 98.0], reference.no_noise)
    day = START + timedelta(days=1)
    assert market.deviation(founded_company(), day) == pytest.approx(
        0.8 * math.log(0.98)
    )


def test_deviation_is_the_same_live_and_after_reload(
    monkeypatch: pytest.MonkeyPatch,
):
    levels = [100.0, 101.0, 99.0, 102.0, 104.0, 103.0]
    company = founded_company()
    days = sessions(len(levels))
    live = market_over(monkeypatch, levels, reference.seeded_noise)
    # Ao vivo o desvio é pedido dia a dia
    live_values = [live.deviation(company, day) for day in days]
    # Depois de recarregar, o pregão do último dia é pedido de uma vez
    reloaded = market_over(monkeypatch, levels, reference.seeded_noise)
    assert reloaded.deviation(company, days[-1]) == live_values[-1]
    assert reloaded.deviation(company, days[2]) == live_values[2]
