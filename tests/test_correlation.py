"""Correlação dos retornos diários entre ativos e o Ibovespa."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from backend.core import repository
from backend.core.dto.correlation import CorrelationCellDTO
from backend.core.dto.series_coverage import OriginCoverageDTO
from backend.core.enum import DataOrigin, IndicatorSeries
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.utils import next_business_day, subtract_months
from backend.features.correlation import correlation
from tests.conftest import SetIndicator

START = date(2023, 1, 2)


def business_days(count: int, start: date = START) -> list[date]:
    days = [start]
    while len(days) < count:
        days.append(next_business_day(days[-1]))
    return days


def levels(days: list[date], returns: list[float]) -> dict[date, float]:
    """Série de preços que parte de 100 e anda pelos retornos dados."""
    values = {days[0]: 100.0}
    for previous, day, change in zip(days, days[1:], returns, strict=False):
        values[day] = values[previous] * (1 + change)
    return values


def wobble(count: int) -> list[float]:
    """Retornos que sobem e descem sem padrão óbvio, entre -2% e +2%."""
    return [((i * 7) % 5 - 2) / 100 for i in range(count)]


@pytest.fixture
def market(monkeypatch: pytest.MonkeyPatch, indicators: SetIndicator):
    """Preços em memória: `market(closes, ibov)` define o que o banco devolveria."""

    def _set(closes: dict[str, dict[date, float]], ibov: dict[date, float]) -> None:
        monkeypatch.setattr(
            repository.stock,
            "get_closes_between",
            lambda tickers, start, end: {
                t: {d: v for d, v in closes[t].items() if start <= d <= end}
                for t in tickers
            },
        )
        monkeypatch.setattr(
            repository.stock,
            "get_coverage",
            lambda: [
                OriginCoverageDTO(
                    key=t, origin=DataOrigin.REAL, start=min(s), end=max(s)
                )
                for t, s in closes.items()
            ],
        )
        indicators(IndicatorSeries.IBOV, {d: Decimal(str(v)) for d, v in ibov.items()})

    return _set


def test_proportional_returns_correlate_at_one_and_opposite_at_minus_one():
    days = business_days(40)
    base = correlation.daily_returns(levels(days, wobble(39)))
    double = correlation.daily_returns(levels(days, [2 * r for r in wobble(39)]))
    mirror = correlation.daily_returns(levels(days, [-r for r in wobble(39)]))

    assert correlation.pair(base, double).correlation == Decimal(1)
    assert correlation.pair(base, mirror).correlation == Decimal(-1)


def test_sample_counts_only_the_days_both_sides_have():
    """Um ativo com 40 pregões e outro com os 25 últimos: 24 retornos em comum."""
    days = business_days(40)
    full = correlation.daily_returns(levels(days, wobble(39)))
    late = correlation.daily_returns(levels(days[15:], wobble(24)))

    cell = correlation.pair(full, late)
    assert cell.days == 24
    assert cell.correlation is not None


def test_short_sample_and_flat_series_have_no_correlation():
    days = business_days(40)
    moving = correlation.daily_returns(levels(days, wobble(39)))
    short = correlation.daily_returns(levels(days[:15], wobble(14)))
    flat = correlation.daily_returns(dict.fromkeys(days, 100.0))

    assert correlation.pair(moving, short) == CorrelationCellDTO(
        correlation=None, days=14
    )
    assert correlation.pair(moving, flat).correlation is None


def test_invalid_price_counts_as_a_day_without_trading():
    """Um fechamento NaN no meio da série: o retorno seguinte cobre os dois dias."""
    days = business_days(4)
    prices = {days[0]: 10.0, days[1]: float("nan"), days[2]: 11.0, days[3]: 12.1}

    returns = correlation.daily_returns(prices)

    assert list(returns) == [days[2], days[3]]
    assert returns[days[2]] == pytest.approx(0.1)


def test_subtract_months_lands_on_the_last_day_of_a_shorter_month():
    assert subtract_months(date(2024, 3, 31), 1) == date(2024, 2, 29)
    assert subtract_months(date(2024, 1, 15), 6) == date(2023, 7, 15)


def test_matrix_is_symmetric_with_ibov_last(market):
    days = business_days(60)
    market(
        {
            "ITUB4": levels(days, wobble(59)),
            "VALE3": levels(days, [-r / 2 for r in wobble(59)]),
        },
        levels(days, [r / 3 for r in wobble(59)]),
    )

    matrix = correlation.build_correlation_matrix(["ITUB4", "VALE3"], "1y", None)

    assert matrix.labels == ["ITUB4", "VALE3", "IBOV"]
    assert matrix.end == days[-1]
    assert matrix.rows[0][0] == CorrelationCellDTO(correlation=Decimal(1), days=59)
    for i in range(3):
        for j in range(3):
            assert matrix.rows[i][j] == matrix.rows[j][i]
    assert matrix.rows[0][1].correlation == Decimal(-1)
    assert matrix.rows[0][2].correlation == Decimal(1)


def test_window_ends_on_the_simulation_date_during_a_match(
    market, monkeypatch: pytest.MonkeyPatch
):
    """Na partida, pedir uma data além da simulação não alcança os preços futuros."""
    days = business_days(80)
    market({"ITUB4": levels(days, wobble(79))}, levels(days, wobble(79)))
    today = days[49]
    monkeypatch.setattr(
        SimulationManager,
        "_active_simulation",
        SimpleNamespace(get_current_date=lambda: today),
    )

    asked_later = correlation.build_correlation_matrix(["ITUB4"], "1y", days[-1])
    asked_none = correlation.build_correlation_matrix(["ITUB4"], "1y", None)

    assert asked_later == asked_none
    assert asked_later.end == today
    assert asked_later.rows[0][0].days == 49

    assets = correlation.build_correlation_assets()
    assert assets.last_date == today
    assert assets.end_fixed is True
