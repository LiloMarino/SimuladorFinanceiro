"""Orçamento do governo: receita pela alíquota, prêmio de risco, dívida e fechamento de mês."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from backend.core.enum import (
    IndicatorSeries,
    InitialAccount,
    MeasureKind,
    MeasureStatus,
)
from backend.core.indicators import annual_index_rate
from backend.features.economy.growth import MacroCourse
from backend.features.government import budget
from backend.features.government.budget import BudgetCourse
from backend.features.government.state import Measure
from backend.features.tax_policy import (
    DEFAULT_TAX_POLICY,
    LossPool,
    SectorRule,
    TaxPolicy,
)
from tests.conftest import SetIndicator
from tests.fakes import daily_series, monthly_series

START = date(2020, 1, 1)


def measure(
    kind: MeasureKind,
    value: str,
    sector: str | None = None,
    segment: str | None = None,
) -> Measure:
    return Measure(
        id=1,
        kind=kind,
        value=Decimal(value),
        before=None,
        sector=sector,
        segment=segment,
        proposer_id=1,
        term_start=START,
        proposed=START,
        status=MeasureStatus.APPROVED,
        effective=START,
    )


def policy_with_common(rate: str) -> TaxPolicy:
    return replace(
        DEFAULT_TAX_POLICY,
        rates={**DEFAULT_TAX_POLICY.rates, LossPool.COMMON: Decimal(rate)},
    )


@pytest.fixture
def flat_economy(indicators: SetIndicator) -> None:
    """SELIC ~14,9% e IPCA ~4,1% ao ano, constantes."""
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2018, 1, 1), date(2030, 1, 1), "0.0551"),
    )
    indicators(IndicatorSeries.IPCA, monthly_series(date(2018, 1, 1), 144, "0.33"))


def course(kind: InitialAccount = InitialAccount.PLAYABLE) -> BudgetCourse:
    return BudgetCourse(
        START,
        lambda _day: DEFAULT_TAX_POLICY,
        budget.initial_account(START, kind),
        MacroCourse(START),
    )


def test_default_policy_collects_sixty_nine_hundredths_of_gdp():
    assert Decimal("0.0069") == budget.DEFAULT_GAME_REVENUE


def test_halving_a_rate_loses_less_than_half_the_revenue():
    """Quem paga menos passa a operar mais: a elasticidade amortece o corte."""
    full = budget.COMMON.revenue(Decimal("0.15"))
    half = budget.COMMON.revenue(Decimal("0.075"))

    assert full / 2 < half < full


def test_zero_rate_collects_nothing():
    assert budget.COMMON.revenue(Decimal(0)) == 0


def test_a_bigger_exemption_limit_shrinks_the_taxed_share():
    assert budget.taxed_share(Decimal(20000)) == 1
    assert budget.taxed_share(Decimal(40000)) < 1
    assert budget.taxed_share(Decimal(0)) > 1


def test_measure_effect_is_the_revenue_difference():
    effect = budget.measure_effect(
        DEFAULT_TAX_POLICY, measure(MeasureKind.DAY_TRADE_RATE, "0.30")
    )

    # 0,03% do PIB x ((30 ÷ 20)^0,7 - 1)
    assert effect == pytest.approx(Decimal("0.0000984604"), abs=Decimal("1e-10"))


def test_sector_exemption_takes_its_slice_of_the_common_tax():
    effect = budget.measure_effect(
        DEFAULT_TAX_POLICY, measure(MeasureKind.SECTOR_EXEMPT, "0", sector="Energia")
    )

    assert effect == -budget.SECTOR_SHARE * budget.COMMON.revenue(Decimal("0.15"))


def test_each_sector_counts_once_by_its_newest_rule():
    policy = replace(
        DEFAULT_TAX_POLICY,
        sector_rules=(
            SectorRule("Energia", None, True),
            SectorRule("Energia", None, False, Decimal("0.05")),
        ),
    )

    sectors = budget.sector_taxes(policy)

    assert len(sectors) == 1
    assert not sectors[0].exempt


def test_premium_is_zero_up_to_half_of_gdp():
    assert budget.premium(Decimal("0.50")) == 0
    assert budget.premium(Decimal("0.30")) == 0


def test_premium_grows_faster_the_higher_the_debt():
    # 2 x (e^(0,02 x 30) - 1) = 1,64 ponto com 80% do PIB
    assert budget.premium(Decimal("0.80")) == pytest.approx(
        Decimal("0.016442"), abs=Decimal("0.000001")
    )
    first = budget.premium(Decimal("0.70")) - budget.premium(Decimal("0.60"))
    second = budget.premium(Decimal("0.90")) - budget.premium(Decimal("0.80"))
    assert second > first


def test_debt_barely_moves_with_zero_primary_when_growth_pays_the_interest():
    debt = budget.step(
        Decimal("0.40"),
        selic=Decimal("0.05"),
        ipca=Decimal("0.03"),
        growth=Decimal("0.02"),
        primary=Decimal(0),
    )

    # Juro de ~5% contra PIB nominal de ~5,06%: a dívida encolhe um fio
    assert debt == pytest.approx(Decimal("0.40"), abs=Decimal("0.001"))


def test_a_primary_deficit_adds_to_the_debt_and_a_surplus_cuts_it():
    rates = {
        "selic": Decimal("0.05"),
        "ipca": Decimal("0.03"),
        "growth": Decimal("0.02"),
    }
    neutral = budget.step(Decimal("0.60"), primary=Decimal(0), **rates)

    assert budget.step(Decimal("0.60"), primary=Decimal("-0.012"), **rates) > neutral
    assert budget.step(Decimal("0.60"), primary=Decimal("0.012"), **rates) < neutral


def test_playable_account_starts_with_zero_primary_and_realistic_with_the_real_one():
    playable = budget.initial_account(date(2017, 1, 2), InitialAccount.PLAYABLE)
    realistic = budget.initial_account(date(2017, 1, 2), InitialAccount.REALISTIC)

    assert playable.debt == realistic.debt == Decimal("0.6984")
    assert playable.primary == 0
    assert realistic.primary < 0


def test_fixed_revenue_closes_the_base_spending_with_the_default_policy():
    account = budget.initial_account(START, InitialAccount.PLAYABLE)

    assert (
        budget.fixed_revenue(account) + budget.DEFAULT_GAME_REVENUE
        == budget.BASE_SPENDING
    )


def test_month_closes_on_its_last_day_and_keeps_the_result(flat_economy: None):
    account = course()

    assert account.months_until(date(2020, 1, 30)) == []
    (january,) = account.months_until(date(2020, 1, 31))

    assert january.month_end == date(2020, 1, 31)
    assert january.closed
    # Na conta jogável o primário é zero; o resultado é só os juros
    assert january.primary == 0
    assert january.result == -january.interest


def test_a_closed_month_is_kept_between_calls(flat_economy: None):
    account = course()
    first = account.months_until(date(2020, 3, 31))

    again = account.months_until(date(2020, 6, 30))

    assert again[: len(first)] == first
    assert len(again) == 6


def test_before_the_first_close_the_course_reports_the_starting_point(
    flat_economy: None,
):
    account = course()

    start = account.latest(START)

    assert not start.closed
    assert start.debt == budget.initial_account(START, InitialAccount.PLAYABLE).debt


def test_a_tax_cut_lowers_revenue_from_the_day_it_takes_effect(flat_economy: None):
    cut = policy_with_common("0.05")
    account = BudgetCourse(
        START,
        lambda day: cut if day >= date(2020, 3, 1) else DEFAULT_TAX_POLICY,
        budget.initial_account(START, InitialAccount.PLAYABLE),
        MacroCourse(START),
    )

    months = account.months_until(date(2020, 4, 30))

    assert months[1].revenue > months[2].revenue


def test_projection_adds_the_revenue_delta_from_the_given_month(flat_economy: None):
    account = course()
    base = account.project(START, date(2020, 6, 30))

    boosted = account.project(
        START, date(2020, 6, 30), Decimal("0.001"), date(2020, 4, 1)
    )

    assert boosted[2].revenue == base[2].revenue
    assert boosted[3].revenue == base[3].revenue + Decimal("0.001")
    assert boosted[-1].debt < base[-1].debt


def test_projection_steps_the_debt_with_the_rates_of_the_day(flat_economy: None):
    account = course()
    initial = account.latest(START)

    (first,) = account.project(START, date(2020, 1, 31))

    # Resultado primário zero, SELIC e IPCA do dia e crescimento na tendência de 2%
    assert first.debt == budget.step(
        initial.debt,
        selic=annual_index_rate(IndicatorSeries.SELIC, START),
        ipca=annual_index_rate(IndicatorSeries.IPCA, START),
        growth=Decimal("0.02"),
        primary=Decimal(0),
    )


def test_premium_curve_runs_from_zero_to_one_and_a_half_of_gdp():
    curve = budget.premium_curve()

    assert curve[0] == (Decimal(0), Decimal(0))
    assert curve[-1][0] == Decimal("1.5")
    assert curve[-1][1] > curve[-2][1]
