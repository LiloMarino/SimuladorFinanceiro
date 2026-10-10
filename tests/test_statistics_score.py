"""Nota geral: faixas por métrica, média por eixo, soma dos eixos (D10)."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.features.statistics.ranking import build_overview
from backend.features.statistics.score import (
    BANDS,
    MIN_SCORE_DAYS,
    build_score,
    player_score,
)
from tests.conftest import SetIndicator

BAND = {band.metric: band for band in BANDS}


def axis_points(score, axis: str):
    return next(a.points for a in score.axes if a.axis == axis)


@pytest.mark.parametrize(
    ("metric", "zero", "hundred"),
    [
        ("return_over_cdi", "-0.10", "0.10"),
        ("max_drawdown", "0.50", "0"),
        ("time_underwater", "252", "0"),
        ("sharpe_ratio", "-1", "2"),
    ],
)
def test_band_ends_are_zero_and_one_hundred_points(metric, zero, hundred):
    band = BAND[metric]

    assert band.points(Decimal(zero)) == 0
    assert band.points(Decimal(hundred)) == 100


def test_points_have_a_floor_and_no_ceiling():
    """Drawdown de 60% não fica negativo; 20 p.p. acima do CDI valem 150."""
    assert BAND["max_drawdown"].points(Decimal("0.60")) == 0
    assert BAND["return_over_cdi"].points(Decimal("0.20")) == 150
    assert BAND["max_drawdown"].points(Decimal("0.20")) == 60


def test_axis_is_the_mean_of_its_measured_metrics():
    """Retorno: 150 e 50 → 100. Sortino sem dado sai da média da Eficiência."""
    score = build_score(
        {
            "return_over_cdi": Decimal("0.20"),
            "return_over_ibov": Decimal("0"),
            "sharpe_ratio": Decimal("0.5"),
            "sortino_ratio": None,
        }
    )

    assert axis_points(score, "return") == 100
    assert axis_points(score, "efficiency") == 50
    assert axis_points(score, "risk") is None
    assert score.total == 150


def test_total_is_the_sum_of_the_decomposition():
    score = build_score(
        {
            "return_over_cdi": Decimal("0.05"),
            "return_over_ibov": Decimal("-0.03"),
            "max_drawdown": Decimal("0.20"),
            "annual_volatility": Decimal("0.16"),
            "time_underwater": Decimal(126),
            "worst_month": Decimal("-0.05"),
            "months_above_cdi": Decimal("0.75"),
            "positive_months": Decimal("0.8"),
            "sharpe_ratio": Decimal("0.5"),
            "sortino_ratio": Decimal("0.8"),
        }
    )

    assert axis_points(score, "risk") == (60 + 60 + 50 + 75) / Decimal(4)
    assert axis_points(score, "consistency") == Decimal("77.5")
    assert score.total == sum(a.points for a in score.axes if a.points is not None)
    for axis in score.axes:
        measured = [m.points for m in axis.metrics if m.points is not None]
        assert axis.points == sum(measured) / len(measured)


def history(networths: list[str]) -> list[PatrimonialHistoryDTO]:
    start = date(2020, 1, 1)
    return [
        PatrimonialHistoryDTO(
            snapshot_date=start + timedelta(days=offset),
            total_networth=Decimal(n),
            total_equity=Decimal(0),
            total_fixed=Decimal(0),
            total_cash=Decimal(n),
            total_contribution=Decimal(0),
        )
        for offset, n in enumerate(networths)
    ]


def test_score_waits_for_the_minimum_sample(indicators: SetIndicator):
    """62 retornos ainda não têm nota; 63 já têm."""
    short = history(["10000"] * MIN_SCORE_DAYS)
    enough = history(["10000"] * (MIN_SCORE_DAYS + 1))

    assert player_score(short) is None
    assert player_score(enough) is not None


def test_ranking_puts_players_without_score_last(indicators: SetIndicator):
    """Quem já tem nota vem antes, mesmo com retorno menor; o retorno desempata."""
    scored = PlayerHistoryDTO(
        player_nickname="Ana",
        simulation_id=1,
        simulation_name="A",
        starting_cash=Decimal("10000"),
        history=history(["10000"] * (MIN_SCORE_DAYS + 1)),
    )
    unscored = PlayerHistoryDTO(
        player_nickname="Lilo",
        simulation_id=2,
        simulation_name="B",
        starting_cash=Decimal("10000"),
        history=history(["10000", "12000"]),
    )

    report = build_overview([unscored, scored])

    assert [p.player_nickname for p in report.players] == ["Ana", "Lilo"]
    assert report.players[1].score is None
    assert report.min_score_days == MIN_SCORE_DAYS
