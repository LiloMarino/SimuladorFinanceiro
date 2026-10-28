"""Painel da economia: pontos mensais, juro real, meta do ano e mudanças da SELIC."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.core.enum import IndicatorSeries
from backend.core.indicators import annualize_daily, inflation_tolerance
from backend.features.economy.panel import build_economy_panel, month_ends
from tests.conftest import SetIndicator

# 0.0551% ao dia compõe, em 252 dias úteis, cerca de 14,9% ao ano
DAILY_LOW = Decimal("0.0551")
# 0.0577% ao dia compõe cerca de 15,6% ao ano: um degrau de uns 0,7 ponto
DAILY_HIGH = Decimal("0.0577")


def test_month_ends_lists_start_each_month_end_and_today():
    assert month_ends(date(2022, 1, 10), date(2022, 3, 15)) == [
        date(2022, 1, 10),
        date(2022, 1, 31),
        date(2022, 2, 28),
        date(2022, 3, 15),
    ]


def test_month_ends_is_a_single_day_before_the_first_session():
    assert month_ends(date(2022, 1, 10), date(2022, 1, 10)) == [date(2022, 1, 10)]


def test_panel_has_real_rate_as_selic_minus_ipca_and_the_year_target(
    indicators: SetIndicator,
):
    indicators(
        IndicatorSeries.SELIC,
        {date(2022, 1, 3): DAILY_LOW, date(2022, 1, 4): DAILY_LOW},
    )
    indicators(IndicatorSeries.IPCA, {date(2022, 1, 1): Decimal("0.5")})

    panel = build_economy_panel(date(2022, 1, 3), date(2022, 1, 4))

    first, last = panel.points
    assert first.date == date(2022, 1, 3)
    assert last.date == date(2022, 1, 4)
    assert first.selic == annualize_daily(DAILY_LOW)
    # Um só mês de IPCA conhecido: 0,5% acumulado
    assert first.ipca == Decimal("0.005")
    assert first.real_rate == first.selic - first.ipca
    # Meta do CMN para 2022
    assert first.target == Decimal("0.035")
    # Tolerância de 1,5 ponto desde 2017
    assert first.tolerance == Decimal("0.015")


def test_panel_marks_the_day_selic_changed_level_and_ignores_noise(
    indicators: SetIndicator,
):
    indicators(
        IndicatorSeries.SELIC,
        {
            date(2022, 1, 3): DAILY_LOW,
            date(2022, 1, 4): DAILY_LOW + Decimal("0.00001"),
            date(2022, 1, 5): DAILY_HIGH,
        },
    )
    indicators(IndicatorSeries.IPCA, {date(2022, 1, 1): Decimal("0.5")})

    panel = build_economy_panel(date(2022, 1, 3), date(2022, 1, 5))

    (change,) = panel.copom_changes
    assert change.date == date(2022, 1, 5)
    # O dia da mudança também é um ponto, para o degrau cair sobre a linha
    assert [point.date for point in panel.points] == [
        date(2022, 1, 3),
        date(2022, 1, 5),
    ]
    assert change.selic == annualize_daily(DAILY_HIGH)
    assert change.change == annualize_daily(DAILY_HIGH) - annualize_daily(DAILY_LOW)


def test_panel_leaves_out_the_days_after_today(indicators: SetIndicator):
    indicators(
        IndicatorSeries.SELIC,
        {
            date(2022, 1, 3): DAILY_LOW,
            date(2022, 1, 4): DAILY_LOW,
            date(2022, 1, 5): DAILY_HIGH,
        },
    )
    indicators(IndicatorSeries.IPCA, {date(2022, 1, 1): Decimal("0.5")})

    panel = build_economy_panel(date(2022, 1, 3), date(2022, 1, 4))

    assert panel.copom_changes == []
    assert panel.points[-1].selic == annualize_daily(DAILY_LOW)


def test_tolerance_was_two_points_until_2016_and_follows_the_year():
    assert inflation_tolerance(date(2010, 6, 1)) == Decimal("0.02")
    assert inflation_tolerance(date(2004, 6, 1)) == Decimal("0.025")
    assert inflation_tolerance(date(2031, 6, 1)) == Decimal("0.015")
