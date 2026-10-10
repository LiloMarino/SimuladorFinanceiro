"""Retorno acumulado da cota e as referências do período (CDI e IBOV)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.enum import IndicatorSeries
from backend.features.statistics import returns, risk
from tests.conftest import SetIndicator
from tests.fakes import daily_series

DAYS = [date(2020, 1, 6), date(2020, 1, 7), date(2020, 1, 8)]


def snapshot(day: date, networth: str, contribution: str = "0"):
    return PatrimonialHistoryDTO(
        snapshot_date=day,
        total_networth=Decimal(networth),
        total_equity=Decimal(0),
        total_fixed=Decimal(0),
        total_cash=Decimal(networth),
        total_contribution=Decimal(contribution),
    )


def test_cumulative_return_starts_at_zero_and_ignores_contributions():
    """+10% e depois um aporte de R$ 1.000 sem rendimento: o acumulado fica em 10%."""
    history = [
        snapshot(DAYS[0], "10000"),
        snapshot(DAYS[1], "11000"),
        snapshot(DAYS[2], "12000", contribution="1000"),
    ]
    series = returns.cumulative_returns(history, risk.daily_returns(history))

    assert series == [
        (DAYS[0], Decimal(0)),
        (DAYS[1], Decimal("0.1")),
        (DAYS[2], Decimal("0.1")),
    ]


def test_cdi_benchmark_compounds_the_daily_rate(indicators: SetIndicator):
    """CDI de 0,04% ao dia: 1,0004 no 2º dia e 1,0004² no 3º."""
    indicators(IndicatorSeries.CDI, daily_series(date(2020, 1, 1), DAYS[-1], "0.04"))
    series = returns.cdi_cumulative(DAYS)

    assert [v for _, v in series] == [
        Decimal(0),
        Decimal("0.0004"),
        Decimal("1.0004") ** 2 - 1,
    ]


def test_ibov_benchmark_is_the_index_variation(indicators: SetIndicator):
    """De 100.000 para 101.000 pontos é +1%; sem pregão no dia vale o último fechamento."""
    indicators(
        IndicatorSeries.IBOV,
        {DAYS[0]: Decimal("100000"), DAYS[1]: Decimal("101000")},
    )
    series = returns.ibov_cumulative(DAYS)

    assert [v for _, v in series] == [Decimal(0), Decimal("0.01"), Decimal("0.01")]


def test_ibov_benchmark_is_empty_without_data(indicators: SetIndicator):
    assert returns.ibov_cumulative(DAYS) == []


def test_annualize_compounds_the_period():
    """+1% em 2 pregões vira 1,01^(252/2) - 1 ao ano."""
    annual = returns.annualize(
        [(DAYS[0], Decimal(0)), (DAYS[1], Decimal(0)), (DAYS[2], Decimal("0.01"))]
    )

    assert annual is not None
    assert float(annual) == pytest.approx(1.01**126 - 1)
