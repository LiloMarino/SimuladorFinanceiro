"""As ligações da economia interligada: sinal e tamanho de cada uma pelo desvio do mês."""

from __future__ import annotations

import math
from datetime import date
from decimal import Decimal

import pytest

from backend.features.economy.links import NO_LINK, LinkMonth, link_month

MONTH = date(2021, 3, 31)


def gap(
    *,
    unemployment: str = "0",
    premium: str = "0",
    gdp: str = "0",
    primary: str = "0",
    change: str = "0",
    consumption: str = "0",
    consumption_change: str = "0",
    corporate: str = "0",
    payroll: str = "0",
    real_rate: str = "0",
    dollar_year_ago: float = 0.0,
) -> LinkMonth:
    return LinkMonth(
        MONTH,
        Decimal(unemployment),
        Decimal(premium),
        Decimal(gdp),
        Decimal(primary),
        Decimal(change),
        consumption_gap=Decimal(consumption),
        consumption_change=Decimal(consumption_change),
        corporate_gap=Decimal(corporate),
        payroll_gap=Decimal(payroll),
        real_rate_gap=Decimal(real_rate),
        dollar_gap_year_ago=dollar_year_ago,
    )


def test_unemployment_two_points_below_history_adds_0_7_point_to_the_ipca():
    link = gap(unemployment="-0.02")

    assert link.phillips_points == pytest.approx(0.7)
    assert link.inflation_points == pytest.approx(0.7)


def test_two_points_of_premium_weigh_on_the_stocks_window_and_not_directly_on_the_ipca():
    link = gap(premium="0.02")

    assert link.premium_points == pytest.approx(2.0)
    assert link.inflation_points == pytest.approx(link.dollar_inflation_points)


def test_two_points_of_premium_lift_the_dollar_by_8_percent():
    link = gap(premium="0.02")

    assert link.dollar_gap == pytest.approx(0.08)
    assert math.exp(link.dollar_gap) == pytest.approx(1.0833, abs=1e-4)


def test_two_points_of_real_rate_above_history_pull_the_dollar_down_by_4_percent():
    link = gap(real_rate="0.02")

    assert link.dollar_real_rate == pytest.approx(-0.04)
    assert link.dollar_gap == pytest.approx(-0.04)


def test_the_dollar_pass_through_counts_the_rise_in_12_months_not_the_level():
    risen = gap(premium="0.02")
    steady = gap(premium="0.02", dollar_year_ago=0.08)

    # Alta de 8,33% em 12 meses repassa 0,07 vezes 8,33 = 0,58 ponto; parado num patamar alto, nada
    assert risen.dollar_inflation_points == pytest.approx(0.5833, abs=1e-3)
    assert steady.dollar_inflation_points == pytest.approx(0.0)


def test_without_deviation_the_dollar_is_the_history_and_passes_nothing_through():
    link = gap()

    assert link.dollar_gap == 0
    assert link.dollar_inflation_points == 0
    assert link.is_zero


def test_the_gdp_level_adds_the_monthly_share_of_the_extra_growth():
    month: LinkMonth | None = None
    for _ in range(12):
        month = link_month(
            month,
            MONTH,
            unemployment_gap=Decimal(0),
            premium_gap=Decimal(0),
            growth_gap=Decimal("0.01"),
            primary_gap=Decimal(0),
            primary_gap_year_ago=Decimal(0),
        )

    # Um ano a 1 ponto acima da história deixa o PIB 1% acima
    assert month is not None
    assert month.gdp_gap == pytest.approx(Decimal("0.01"))


def test_the_cycle_collects_with_the_gdp_and_pays_insurance_with_the_unemployment():
    assert gap(gdp="0.02").cycle_revenue == Decimal("0.0012")
    assert gap(unemployment="0.02").insurance == Decimal("0.001")


def test_the_primary_worsening_in_a_year_pushes_growth_by_half_of_it():
    # Um corte de imposto de 1% do PIB soma meio ponto ao alvo do crescimento
    assert gap(change="-0.01").impulse == Decimal("0.005")
    assert gap(change="0.01").impulse == Decimal("-0.005")


def test_premium_above_history_takes_three_quarters_of_it_from_the_growth_aim():
    # Prêmio 2 pontos acima da história encarece o crédito e tira 1,5 ponto do alvo
    assert gap(premium="0.02").crowding_out == Decimal("-0.015")
    # Prêmio abaixo da história não empurra o crescimento
    assert gap(premium="-0.02").crowding_out == 0
    assert gap().crowding_out == 0


def test_a_deficit_that_stays_put_for_a_year_stops_pushing():
    cut = link_month(
        None,
        MONTH,
        unemployment_gap=Decimal(0),
        premium_gap=Decimal(0),
        growth_gap=Decimal(0),
        primary_gap=Decimal("-0.01"),
        primary_gap_year_ago=Decimal(0),
    )
    kept = link_month(
        cut,
        MONTH,
        unemployment_gap=Decimal(0),
        premium_gap=Decimal(0),
        growth_gap=Decimal(0),
        primary_gap=Decimal("-0.01"),
        primary_gap_year_ago=Decimal("-0.01"),
    )

    assert cut.impulse == Decimal("0.005")
    assert kept.impulse == 0
    assert not kept.is_zero


def test_no_deviation_has_no_effect():
    assert NO_LINK.is_zero
    assert NO_LINK.inflation_points == 0
    assert NO_LINK.impulse == 0
    assert gap().same_effect(NO_LINK)
    assert not gap(premium="0.001").same_effect(NO_LINK)


def test_a_dearer_consumption_tax_passes_half_of_its_change_to_prices():
    # Dois pontos a mais de alíquota em 12 meses somam um ponto ao IPCA
    link = gap(consumption="0.02", consumption_change="0.02")

    assert link.consumption_points == pytest.approx(1.0)
    assert link.inflation_points == pytest.approx(1.0)
    # Alíquota alta mantida por um ano não pressiona mais os preços
    kept = gap(consumption="0.02", consumption_change="0")
    assert kept.consumption_points == 0
    assert not kept.same_effect(NO_LINK)


def test_the_consumption_tax_change_is_the_gap_against_a_year_ago():
    month = link_month(
        None,
        MONTH,
        unemployment_gap=Decimal(0),
        premium_gap=Decimal(0),
        growth_gap=Decimal(0),
        primary_gap=Decimal(0),
        primary_gap_year_ago=Decimal(0),
        consumption_gap=Decimal("0.03"),
        consumption_gap_year_ago=Decimal("0.01"),
    )

    assert month.consumption_change == Decimal("0.02")


def test_the_corporate_tax_above_the_default_pulls_the_stocks_down():
    # Dez pontos acima do padrão tiram 12% do expoente da bolsa; a redução levanta
    assert gap(corporate="0.10").corporate_points == pytest.approx(-0.12)
    assert gap(corporate="-0.10").corporate_points == pytest.approx(0.12)
    assert gap(corporate="0.10").inflation_points == 0


def test_the_payroll_tax_adds_to_the_unemployment_per_year():
    # Dois pontos de alíquota a mais somam 0,12 ponto de desemprego ao ano
    assert gap(payroll="0.02").payroll_jobs == Decimal("0.0012")
    assert gap(payroll="-0.02").payroll_jobs == Decimal("-0.0012")
    assert gap().payroll_jobs == 0
