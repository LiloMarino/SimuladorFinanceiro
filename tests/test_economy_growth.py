"""Crescimento e desemprego do país: o alvo pelo juro real e pela bolsa, o passo mensal e o fechamento de mês."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.enum import IndicatorSeries
from backend.core.indicators import annual_index_rate, last_known_value
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
    # Bolsa em +20% em 12 meses com IPCA de 4% (0,33% ao mês): a alta real, de 15,3%,
    # fica 10,3 pontos acima do neutro de 5% e soma 0,52 ponto
    ipca = Decimal("1.0033") ** 12 - 1
    assert aim.stocks is not None
    assert aim.stocks == pytest.approx(Decimal("1.2") / (1 + ipca) - 1)
    assert aim.stocks_part == growth.STOCKS_WEIGHT * (
        aim.stocks - growth.NEUTRAL_STOCKS
    )
    assert round(aim.stocks_part, 4) == Decimal("0.0052")


def test_aim_from_gives_the_aim_that_growth_aim_reads_from_the_series(
    flat_economy: None,
):
    day = date(2020, 6, 30)
    read = growth.growth_aim(day, Decimal("0.01"), Decimal("0.002"))
    ibov_now = last_known_value(IndicatorSeries.IBOV, day)
    ibov_before = last_known_value(
        IndicatorSeries.IBOV, day - timedelta(days=growth.STOCKS_WINDOW_DAYS)
    )

    assert (
        growth.aim_from(
            annual_index_rate(IndicatorSeries.SELIC, day),
            annual_index_rate(IndicatorSeries.IPCA, day),
            ibov_now / ibov_before - 1
            if ibov_now is not None and ibov_before
            else None,
            Decimal("0.01"),
            Decimal("0.002"),
        )
        == read
    )


def test_growth_step_goes_a_quarter_of_the_way_and_stays_in_the_band():
    assert growth.step_growth(Decimal("0.02"), Decimal("0.06")) == Decimal("0.03")
    assert growth.step_growth(growth.MAX_GROWTH, Decimal("1")) == growth.MAX_GROWTH
    assert growth.step_growth(growth.MIN_GROWTH, Decimal("-1")) == growth.MIN_GROWTH


def test_unemployment_step_follows_okun_and_stays_in_the_band():
    above_trend = growth.step_unemployment(Decimal("0.10"), Decimal("0.05"))

    # Meio ponto de desemprego a menos por ano para cada ponto acima da tendência
    assert above_trend == Decimal("0.10") - Decimal("0.5") * Decimal("0.03") / 12
    assert (
        growth.step_unemployment(growth.MIN_UNEMPLOYMENT, Decimal("0.08"))
        == growth.MIN_UNEMPLOYMENT
    )


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
    built.use_government(lambda _day: Decimal("0.006"), lambda _day: Decimal(0))
    assert (
        built.latest(date(2020, 12, 31)).growth
        > plain.latest(date(2020, 12, 31)).growth
    )


def test_growth_stays_inside_the_clamp_when_stocks_crash(indicators: SetIndicator):
    """Ibovespa caindo pela metade todo ano com juro real altíssimo: o PIB para no piso."""
    indicators(
        IndicatorSeries.SELIC, daily_series(date(2018, 1, 1), date(2030, 1, 1), "0.1")
    )
    indicators(IndicatorSeries.IPCA, monthly_series(date(2018, 1, 1), 144, "0.1"))
    indicators(
        IndicatorSeries.IBOV,
        {date(2018 + year, 1, 1): Decimal(100000) / 2**year for year in range(12)},
    )
    course = MacroCourse(START)

    months = course.months_until(date(2028, 12, 31))

    assert months[-1].aim.value < growth.MIN_GROWTH
    assert min(m.growth for m in months) == growth.MIN_GROWTH


def test_the_base_follows_the_recorded_series_and_the_game_matches_it(
    flat_economy: None, indicators: SetIndicator
):
    indicators(
        IndicatorSeries.GDP_GROWTH,
        {date(2020, month, 1): Decimal("-3.5") for month in (1, 4, 7, 10)},
    )
    indicators(IndicatorSeries.UNEMPLOYMENT, monthly_series(START, 12, "13.5"))

    months = MacroCourse(START).months_until(date(2020, 12, 31))

    # A queda de 2020 fica como foi, mesmo abaixo da faixa do modelo
    for month in months:
        assert month.base_growth == Decimal("-0.035")
        assert month.base_unemployment == Decimal("0.135")
        assert (month.growth, month.unemployment) == (
            month.base_growth,
            month.base_unemployment,
        )


def test_before_the_unemployment_series_starts_the_model_runs(
    flat_economy: None, indicators: SetIndicator
):
    indicators(IndicatorSeries.UNEMPLOYMENT, monthly_series(date(2020, 4, 1), 9, "12"))

    months = MacroCourse(START).months_until(date(2020, 6, 30))

    # Juro real alto puxa o crescimento abaixo da tendência e o desemprego sobe
    assert months[0].base_unemployment > growth.NEUTRAL_UNEMPLOYMENT
    assert months[2].base_unemployment > months[0].base_unemployment
    later = MacroCourse(START).latest(date(2020, 4, 30))
    assert later.base_unemployment == Decimal("0.12")


def test_the_impulse_pushes_the_game_away_from_the_history(flat_economy: None):
    course = MacroCourse(START)
    course.use_government(growth.no_push, lambda _day: Decimal("0.01"))

    month = course.latest(date(2020, 12, 31))

    assert month.gap.impulse > 0
    assert month.growth == month.base_growth + month.gap.total
    assert month.unemployment < month.base_unemployment
