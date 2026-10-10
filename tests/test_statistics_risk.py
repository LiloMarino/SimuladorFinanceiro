from __future__ import annotations

import math
from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.enum import IndicatorSeries
from backend.features.statistics.ranking import build_performance_report
from backend.features.statistics.risk import build_risk_metrics
from tests.conftest import SetIndicator
from tests.fakes import daily_series

START = date(2020, 1, 1)


def history(*days: str | tuple[str, str]) -> list[PatrimonialHistoryDTO]:
    """Um snapshot por dia: patrimônio, ou (patrimônio, aporte acumulado)."""
    snapshots = []
    for offset, day in enumerate(days):
        networth, contribution = day if isinstance(day, tuple) else (day, "0")
        snapshots.append(
            PatrimonialHistoryDTO(
                snapshot_date=START + timedelta(days=offset),
                total_networth=Decimal(networth),
                total_equity=Decimal(0),
                total_fixed=Decimal(0),
                total_cash=Decimal(networth),
                total_contribution=Decimal(contribution),
            )
        )
    return snapshots


@pytest.fixture(autouse=True)
def no_database(indicators: SetIndicator):
    """O CDI vem de séries em memória; sem `cdi(...)`, a série fica vazia."""


@pytest.fixture
def cdi(indicators: SetIndicator):
    """Fixa o CDI diário (em % ao dia) no período dos snapshots."""

    def set_rate(rate: str) -> None:
        indicators(
            IndicatorSeries.CDI,
            daily_series(START - timedelta(days=7), START + timedelta(days=30), rate),
        )

    return set_rate


def test_api_reports_drawdown_from_peak_to_trough():
    """Aceite do F11: pico de R$ 15.000 e vale de R$ 12.000 dão drawdown de 20%."""
    player = PlayerHistoryDTO(
        player_nickname="Lilo",
        simulation_id=1,
        simulation_name="Simulação #1",
        starting_cash=Decimal("10000"),
        history=history("10000", "15000", "12000"),
    )

    report = build_performance_report([player])

    assert report.players[0].risk.max_drawdown == Decimal("0.2")


def test_contribution_does_not_hide_a_drop():
    """O aporte que repõe a queda não conta como recuperação: o drawdown continua 20%."""
    risk = build_risk_metrics(history("10000", "15000", ("15000", "3000")))

    assert risk.max_drawdown == Decimal("0.2")


def test_contribution_alone_is_not_return():
    """Patrimônio que só cresceu pelo aporte não rende nem cai."""
    risk = build_risk_metrics(history("10000", ("11000", "1000"), ("12000", "2000")))

    assert risk.max_drawdown == Decimal("0")
    assert risk.annual_volatility == Decimal("0")


def test_flat_series_has_no_volatility_and_no_sharpe():
    """Sem oscilação não há risco para dividir: o Sharpe fica indefinido."""
    risk = build_risk_metrics(history("10000", "10000", "10000"))

    assert risk.annual_volatility == Decimal("0")
    assert risk.sharpe_ratio is None


def test_volatility_and_sharpe_of_a_known_series(cdi):
    """Retornos de +2% e -1%: média 0,5%, desvio-padrão 0,015·√2, anualizados por 252."""
    cdi("0.04")
    risk = build_risk_metrics(history("10000", "10200", "10098"))

    volatility = 0.015 * math.sqrt(2) * math.sqrt(252)
    cdi_daily = 0.0004
    assert risk.annual_volatility is not None and risk.sharpe_ratio is not None
    assert float(risk.annual_volatility) == pytest.approx(volatility)
    assert float(risk.sharpe_ratio) == pytest.approx(
        (0.005 - cdi_daily) * 252 / volatility
    )


def test_short_series_leaves_metrics_undefined():
    """Um dia não tem retorno; dois dias têm um retorno, o que não basta para medir oscilação."""
    one_day = build_risk_metrics(history("10000"))
    two_days = build_risk_metrics(history("10000", "9000"))

    assert (one_day.max_drawdown, one_day.annual_volatility, one_day.sharpe_ratio) == (
        None,
        None,
        None,
    )
    assert two_days.max_drawdown == Decimal("0.1")
    assert (two_days.annual_volatility, two_days.sharpe_ratio) == (None, None)
