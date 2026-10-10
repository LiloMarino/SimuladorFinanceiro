from __future__ import annotations

import math
from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.enum import IndicatorSeries
from backend.features.statistics import risk
from backend.features.statistics.report import build_risk_report
from tests.conftest import SetIndicator
from tests.fakes import daily_series

START = date(2020, 1, 1)


def history(
    *days: str | tuple[str, str], start: date = START
) -> list[PatrimonialHistoryDTO]:
    """Um snapshot por dia: patrimônio, ou (patrimônio, aporte acumulado)."""
    snapshots = []
    for offset, day in enumerate(days):
        networth, contribution = day if isinstance(day, tuple) else (day, "0")
        snapshots.append(
            PatrimonialHistoryDTO(
                snapshot_date=start + timedelta(days=offset),
                total_networth=Decimal(networth),
                total_equity=Decimal(0),
                total_fixed=Decimal(0),
                total_cash=Decimal(networth),
                total_contribution=Decimal(contribution),
            )
        )
    return snapshots


def returns_of(*days: str | tuple[str, str]) -> risk.DailyReturns:
    return risk.daily_returns(history(*days))


@pytest.fixture(autouse=True)
def no_database(indicators: SetIndicator):
    """O CDI vem de séries em memória; sem `cdi(...)`, a série fica vazia."""


@pytest.fixture
def cdi(indicators: SetIndicator):
    """Fixa o CDI diário (em % ao dia) no período dos snapshots."""

    def set_rate(rate: str) -> None:
        indicators(
            IndicatorSeries.CDI,
            daily_series(START - timedelta(days=7), START + timedelta(days=90), rate),
        )

    return set_rate


def test_api_reports_drawdown_from_peak_to_trough(monkeypatch: pytest.MonkeyPatch):
    """Aceite do F11: pico de R$ 15.000 e vale de R$ 12.000 dão drawdown de 20%."""
    player = PlayerHistoryDTO(
        player_nickname="Lilo",
        simulation_id=1,
        simulation_name="Simulação #1",
        starting_cash=Decimal("10000"),
        history=history("10000", "15000", "12000"),
    )
    monkeypatch.setattr(
        repository.statistics, "get_players_history", lambda _ids: [player]
    )

    report = build_risk_report([1])

    assert report.players[0].max_drawdown == Decimal("0.2")
    assert [p.value for p in report.players[0].drawdown] == [0, Decimal("0.2")]


def test_contribution_does_not_hide_a_drop():
    """O aporte que repõe a queda não conta como recuperação: o drawdown continua 20%."""
    days = returns_of("10000", "15000", ("15000", "3000"))

    assert risk.max_drawdown(days) == Decimal("0.2")


def test_contribution_alone_is_not_return():
    """Patrimônio que só cresceu pelo aporte não rende nem cai."""
    days = returns_of("10000", ("11000", "1000"), ("12000", "2000"))

    assert risk.max_drawdown(days) == Decimal("0")
    assert risk.annual_volatility([r for _, r in days]) == Decimal("0")


def test_flat_series_has_no_volatility_and_no_sharpe():
    """Sem oscilação não há risco para dividir: Sharpe e Sortino ficam indefinidos."""
    days = returns_of("10000", "10000", "10000")
    volatility = risk.annual_volatility([r for _, r in days])

    assert volatility == Decimal("0")
    assert risk.sharpe_ratio(days, volatility) is None
    assert risk.sortino_ratio(days) is None


def test_volatility_and_sharpe_of_a_known_series(cdi):
    """Retornos de +2% e -1%: média 0,5%, desvio-padrão 0,015·√2, anualizados por 252."""
    cdi("0.04")
    days = returns_of("10000", "10200", "10098")
    volatility = risk.annual_volatility([r for _, r in days])
    sharpe = risk.sharpe_ratio(days, volatility)

    expected_volatility = 0.015 * math.sqrt(2) * math.sqrt(252)
    cdi_daily = 0.0004
    assert volatility is not None and sharpe is not None
    assert float(volatility) == pytest.approx(expected_volatility)
    assert float(sharpe) == pytest.approx(
        (0.005 - cdi_daily) * 252 / expected_volatility
    )


def test_sortino_counts_only_days_below_cdi(cdi):
    """
    Excessos sobre o CDI de +1,96% e -1,04%: o desvio para baixo é
    √((0² + 0,0104²) ÷ 2) e só ele entra no denominador.
    """
    cdi("0.04")
    days = returns_of("10000", "10200", "10098")
    sortino = risk.sortino_ratio(days)

    downside = math.sqrt(0.0104**2 / 2) * math.sqrt(252)
    assert sortino is not None
    assert float(sortino) == pytest.approx((0.005 - 0.0004) * 252 / downside)


def test_short_series_leaves_metrics_undefined():
    """Um dia não tem retorno; dois dias têm um retorno, o que não basta para medir oscilação."""
    one_day = returns_of("10000")
    two_days = returns_of("10000", "9000")

    assert risk.max_drawdown(one_day) is None
    assert risk.time_underwater(one_day) is None
    assert risk.annual_return(one_day) is None
    assert risk.max_drawdown(two_days) == Decimal("0.1")
    assert risk.annual_volatility([r for _, r in two_days]) is None
    assert risk.sortino_ratio(two_days) is None


def test_time_underwater_is_the_longest_stretch_below_the_peak():
    """Cai no 2º dia e só volta ao topo no 5º: três pregões abaixo do pico."""
    days = returns_of("100", "110", "100", "105", "108", "111", "105")

    assert risk.time_underwater(days) == 3
    assert [round(d, 4) for _, d in risk.drawdown_series(days)] == [
        0,
        Decimal("0.0909"),
        Decimal("0.0455"),
        Decimal("0.0182"),
        0,
        Decimal("0.0541"),
    ]


def test_rolling_volatility_starts_after_a_full_window():
    """Com janela de 3 pregões, a primeira volatilidade sai no 3º retorno."""
    days = returns_of("100", "102", "101", "104", "103")
    rolling = risk.rolling_volatility(days, window=3)

    assert [day for day, _ in rolling] == [days[2][0], days[3][0]]
    first = risk.annual_volatility([r for _, r in days[:3]])
    assert rolling[0][1] == first


def test_annual_return_compounds_the_quota():
    """+1% ao dia em 2 pregões vira (1,01²)^(252/2) - 1."""
    days = returns_of("100", "101", "102.01")
    annual = risk.annual_return(days)

    assert annual is not None
    assert float(annual) == pytest.approx(1.01**252 - 1)


def test_monthly_returns_compound_days_and_cdi_by_calendar_month(cdi):
    """Janeiro sobe 10% e fevereiro cai 5%; o CDI de cada mês é composto dia a dia."""
    cdi("0.04")
    snapshots = [
        *history("100", "110", start=date(2020, 1, 30)),
        *history("104.5", start=date(2020, 2, 3)),
    ]
    months = risk.monthly_returns(risk.daily_returns(snapshots))

    assert [(m.month, m.value) for m in months] == [
        (date(2020, 1, 1), Decimal("0.1")),
        (date(2020, 2, 1), Decimal("-0.05")),
    ]
    assert months[0].cdi == Decimal("0.0004")
