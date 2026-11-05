"""As ligações da economia interligada: sinal e tamanho de cada uma pelo desvio do mês."""

from __future__ import annotations

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
) -> LinkMonth:
    return LinkMonth(
        MONTH,
        Decimal(unemployment),
        Decimal(premium),
        Decimal(gdp),
        Decimal(primary),
        Decimal(change),
    )


def test_unemployment_two_points_below_history_adds_0_7_point_to_the_ipca():
    link = gap(unemployment="-0.02")

    assert link.phillips_points == pytest.approx(0.7)
    assert link.inflation_points == pytest.approx(0.7)


def test_two_points_of_premium_add_one_point_to_the_ipca_and_two_to_the_stocks_window():
    link = gap(premium="0.02")

    assert link.premium_points == pytest.approx(2.0)
    assert link.premium_inflation_points == pytest.approx(1.0)
    assert link.inflation_points == pytest.approx(1.0)


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
