"""Crescimento e desemprego do país: o alvo pelo juro real e pela bolsa, o passo mensal e o fechamento de mês."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.enum import IndicatorSeries
from backend.features.economy import growth
from backend.features.economy.growth import MacroCourse
from tests.conftest import SetIndicator
from tests.fakes import daily_series, monthly_series

START = date(2020, 1, 1)
# 0.0551% ao dia compõe cerca de 14,9% ao ano
SELIC_DAILY = "0.0551"


@pytest.fixture
def flat_economy(indicators: SetIndicator) -> None:
    """SELIC em ~14,9% e IPCA em ~4,1% ao ano; sem série de bolsa."""
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2018, 1, 1), date(2024, 1, 1), SELIC_DAILY),
    )
    indicators(IndicatorSeries.IPCA, monthly_series(date(2018, 1, 1), 72, "0.33"))


def test_aim_is_the_trend_when_real_rate_is_neutral_and_stocks_are_flat(
    indicators: SetIndicator,
):
    """Juro real de 5% e sem série de bolsa: o alvo é a tendência de 2%."""
    # SELIC = IPCA + 5 pontos fecha o juro real neutro
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2018, 1, 1), date(2024, 1, 1), SELIC_DAILY),
    )
    indicators(IndicatorSeries.IPCA, monthly_series(date(2018, 1, 1), 72, "0.8"))

    aim = growth.growth_aim(date(2020, 6, 30))

    assert aim.trend == Decimal("0.02")
    assert aim.stocks is None
    assert aim.stocks_part == 0
    # Cada ponto de juro real acima do neutro tira 0,4 ponto do alvo
    assert aim.real_rate_part == -growth.REAL_RATE_WEIGHT * (
        aim.real_rate - growth.NEUTRAL_REAL_RATE
    )
    assert aim.value == aim.trend + aim.real_rate_part


def test_high_real_rate_pulls_the_aim_down_and_stocks_push_it_up(
    indicators: SetIndicator,
):
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2018, 1, 1), date(2024, 1, 1), SELIC_DAILY),
    )
    indicators(IndicatorSeries.IPCA, monthly_series(date(2018, 1, 1), 72, "0.33"))
    indicators(
        IndicatorSeries.IBOV,
        {date(2019, 6, 28): Decimal(100000), date(2020, 6, 30): Decimal(120000)},
    )

    aim = growth.growth_aim(date(2020, 6, 30))

    # Juro real de ~10,4%: bem acima do neutro de 5%
    assert aim.real_rate_part < 0
    # Bolsa em +20% em 12 meses: 15 pontos acima do neutro de 5%, a 5 pontos de crescimento cada
    assert aim.stocks == Decimal("0.2")
    assert aim.stocks_part == Decimal("0.75")


def test_month_closes_only_on_its_last_day(flat_economy: None):
    course = MacroCourse(START)

    assert course.months_until(date(2020, 1, 30)) == []
    closed = course.months_until(date(2020, 1, 31))

    assert [m.month_end for m in closed] == [date(2020, 1, 31)]


def test_growth_moves_a_quarter_of_the_way_to_the_aim_each_month(flat_economy: None):
    course = MacroCourse(START)

    first = course.months_until(date(2020, 1, 31))[0]

    assert first.growth == growth.TREND + growth.GROWTH_STEP * (
        first.aim.value - growth.TREND
    )


def test_unemployment_falls_when_growth_beats_the_trend(indicators: SetIndicator):
    # Juro real zero (SELIC = IPCA): o alvo passa da tendência e o desemprego cai
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2018, 1, 1), date(2024, 1, 1), "0.0158"),
    )
    indicators(IndicatorSeries.IPCA, monthly_series(date(2018, 1, 1), 72, "0.33"))
    course = MacroCourse(START)

    months = course.months_until(date(2020, 12, 31))

    assert months[-1].growth > growth.TREND
    assert months[-1].unemployment < growth.NEUTRAL_UNEMPLOYMENT


def test_unemployment_stays_inside_the_clamp(indicators: SetIndicator):
    # Juro real altíssimo mantém o crescimento negativo por anos
    indicators(
        IndicatorSeries.SELIC, daily_series(date(2018, 1, 1), date(2040, 1, 1), "0.1")
    )
    indicators(IndicatorSeries.IPCA, monthly_series(date(2018, 1, 1), 240, "0.1"))
    course = MacroCourse(START)

    months = course.months_until(date(2038, 12, 31))

    assert max(m.unemployment for m in months) == growth.MAX_UNEMPLOYMENT


def test_a_closed_month_never_changes(flat_economy: None):
    course = MacroCourse(START)
    before = course.months_until(date(2020, 3, 31))

    after = course.months_until(date(2020, 6, 30))

    assert after[: len(before)] == before


def test_before_the_first_close_the_country_is_at_the_starting_point(
    flat_economy: None,
):
    course = MacroCourse(START)

    start = course.latest(START)

    assert start.growth == growth.TREND
    assert start.unemployment == growth.NEUTRAL_UNEMPLOYMENT


def test_works_add_their_part_to_the_aim_and_the_growth_climbs_toward_it(
    flat_economy: None,
):
    without = growth.growth_aim(date(2020, 6, 30))
    with_works = growth.growth_aim(date(2020, 6, 30), Decimal("0.006"))

    assert with_works.spending_part == Decimal("0.006")
    assert with_works.value == without.value + Decimal("0.006")

    plain = MacroCourse(START)
    built = MacroCourse(START)
    built.use_spending(lambda _day: Decimal("0.006"))
    assert (
        built.latest(date(2020, 12, 31)).growth
        > plain.latest(date(2020, 12, 31)).growth
    )
