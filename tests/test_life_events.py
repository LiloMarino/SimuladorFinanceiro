from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from backend.core.enum import IndicatorSeries, LifeEventEffect
from backend.core.life_budget import LifeBudget
from backend.core.utils import next_business_day
from backend.features.simulation.life_events import (
    LIFE_EVENTS,
    LifeEventType,
    layoff_factor_of,
    net_salary,
    overdraft_interest,
    salary_skipped,
    unexpected_on,
)
from backend.features.tax_policy import DEFAULT_TAX_POLICY
from tests.conftest import SetIndicator
from tests.fakes import monthly_series

START = date(2020, 1, 2)


def trading_days(start: date, count: int) -> list[date]:
    days = [start]
    while len(days) < count:
        days.append(next_business_day(days[-1]))
    return days


YEARS = trading_days(START, 252 * 20)


def draws(seed: int, per_year: int, events=LIFE_EVENTS) -> list:
    return [unexpected_on(seed, day, per_year, events) for day in YEARS]


def test_same_seed_draws_the_same_events_for_everyone_and_on_resume():
    assert draws(7, 6) == draws(7, 6)


def test_another_seed_draws_other_events():
    assert draws(7, 6) != draws(8, 6)


@pytest.mark.parametrize("per_year", [1, 3, 6])
def test_average_frequency_follows_the_setting(per_year: int):
    """Em 20 anos, a média anual de imprevistos fica perto da frequência escolhida."""
    per_simulated_year = sum(e is not None for e in draws(42, per_year)) / 20

    assert per_simulated_year == pytest.approx(per_year, rel=0.25)


def test_no_events_when_the_frequency_is_none():
    assert all(e is None for e in draws(42, 0))


def test_a_layoff_skips_the_salary_of_the_next_month():
    layoff = next(
        (day, event)
        for day in YEARS
        if (event := unexpected_on(3, day, 6)) and event.key == "LAYOFF"
    )
    day = layoff[0]
    next_month = date(day.year + day.month // 12, day.month % 12 + 1, 1)

    assert salary_skipped(3, next_month, 6, START)


def test_a_month_without_layoff_pays_the_salary():
    assert not salary_skipped(3, date(2020, 2, 1), 0, START)


def test_a_new_event_type_is_drawn_without_touching_the_engine():
    """O registro é a única fonte: um tipo novo, sozinho na tupla, é o único sorteado."""
    car = LifeEventType(
        key="CAR",
        label="Multa",
        effect=LifeEventEffect.CASH_OUT,
        weight=1,
        expense_multiple=Decimal("0.5"),
    )

    drawn = {e for e in draws(42, 6, (car,)) if e is not None}

    assert drawn == {car}


def budget(inflation_adjusted: bool, growth: str | None = None) -> LifeBudget:
    life = LifeBudget(
        monthly_salary=Decimal(5000),
        monthly_expense=Decimal(3000),
        withdrawal_rate=Decimal("0.04"),
        inflation_adjusted=inflation_adjusted,
        start_date=START,
    )
    if growth is None:
        return life
    return replace(life, growth_on=lambda _day: Decimal(growth))


def test_goal_is_25_times_the_yearly_expense_at_4_percent():
    assert budget(False).goal_on(START) == Decimal(900000)


def test_salary_expense_and_goal_rise_by_ipca_once_a_year(indicators: SetIndicator):
    # 1% ao mês por 12 meses: ~12,68% acumulados no ano
    indicators(IndicatorSeries.IPCA, monthly_series(date(2019, 1, 1), 36, "1"))
    life = budget(True)
    growth = Decimal("1.01") ** 12

    cent = Decimal("0.01")

    assert life.expense_on(date(2021, 1, 1)) == Decimal(3000)
    assert life.expense_on(date(2021, 1, 4)) == (3000 * growth).quantize(cent)
    assert life.salary_on(date(2021, 6, 1)) == (5000 * growth).quantize(cent)
    # A meta do 2º ano: 25x a despesa anual já reajustada duas vezes
    assert life.goal_on(date(2022, 1, 3)) == 300 * (3000 * growth**2).quantize(cent)
    assert life.readjustments(date(2022, 1, 3)) == [
        START,
        date(2021, 1, 2),
        date(2022, 1, 2),
    ]


def test_overdraft_pays_8_percent_a_month_compounded_by_trading_day():
    cash = Decimal(-1000)
    rate = Decimal("0.08")
    balance = cash
    for _ in range(21):
        balance -= overdraft_interest(balance, rate)

    assert overdraft_interest(Decimal(10), rate) == 0
    # 21 pregões são 1/12 de 252: o mês fecha em 8%
    assert balance == pytest.approx(Decimal(-1080), rel=Decimal("0.001"))


def layoffs(seed: int, unemployment: str) -> int:
    factor = layoff_factor_of(Decimal(unemployment))
    return sum(
        (event := unexpected_on(seed, day, 6, layoff_factor=factor)) is not None
        and event.effect is LifeEventEffect.SKIP_NEXT_SALARY
        for day in YEARS
    )


def test_layoff_chance_follows_unemployment():
    """Na mesma semente, desemprego de 18% (o dobro do neutro) demite mais que o de 4%."""
    assert layoff_factor_of(Decimal("0.09")) == pytest.approx(1)
    assert layoff_factor_of(Decimal("0.18")) == pytest.approx(2)
    assert layoffs(42, "0.18") > layoffs(42, "0.09") > layoffs(42, "0.04")


def test_unemployment_changes_only_the_layoff_chance():
    high = draws_with_factor(42, 2.0)
    neutral = draws_with_factor(42, 1.0)

    def others(drawn: list) -> list:
        return [
            e if e is None or e.effect is not LifeEventEffect.SKIP_NEXT_SALARY else None
            for e in drawn
        ]

    # Os outros tipos mantêm o dia e o tipo sorteados; só a fatia da demissão cresce
    assert [e for e in others(high) if e] == [e for e in others(neutral) if e]


def draws_with_factor(seed: int, factor: float) -> list:
    return [unexpected_on(seed, day, 6, layoff_factor=factor) for day in YEARS]


def test_layoff_draw_is_deterministic_with_the_unemployment_factor():
    assert draws_with_factor(7, 1.7) == draws_with_factor(7, 1.7)


def test_salary_rises_by_ipca_plus_half_the_gdp_growth(indicators: SetIndicator):
    # IPCA acumulado de ~12,68% e PIB de 3%: o salário sobe 12,68% + 1,5%
    indicators(IndicatorSeries.IPCA, monthly_series(date(2019, 1, 1), 36, "1"))
    ipca = Decimal("1.01") ** 12 - 1
    life = budget(True, growth="0.03")

    assert life.salary_on(date(2021, 6, 1)) == (
        5000 * (1 + ipca + Decimal("0.015"))
    ).quantize(Decimal("0.01"))
    # A despesa e a meta seguem só o IPCA
    assert life.expense_on(date(2021, 6, 1)) == (3000 * (1 + ipca)).quantize(
        Decimal("0.01")
    )


def test_salary_gets_no_real_raise_in_a_recession(indicators: SetIndicator):
    indicators(IndicatorSeries.IPCA, monthly_series(date(2019, 1, 1), 36, "1"))
    ipca = Decimal("1.01") ** 12 - 1

    life = budget(True, growth="-0.04")

    assert life.salary_on(date(2021, 6, 1)) == (5000 * (1 + ipca)).quantize(
        Decimal("0.01")
    )


def test_salary_stays_fixed_without_inflation_adjustment():
    assert budget(False, growth="0.05").salary_on(date(2022, 6, 1)) == Decimal(5000)


def test_income_tax_above_the_reference_discounts_the_salary():
    reference = DEFAULT_TAX_POLICY.personal_rate

    assert net_salary(Decimal(8000), reference) == Decimal(8000)
    # 5 pontos acima da referência descontam 5% do salário; abaixo, somam
    assert net_salary(Decimal(8000), reference + Decimal("0.05")) == Decimal(7600)
    assert net_salary(Decimal(8000), reference - Decimal("0.05")) == Decimal(8400)
