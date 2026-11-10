from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from backend.core.enum import IncomeLoss, IndicatorSeries, Profession
from backend.core.life_budget import LifeBudget
from backend.core.professions import (
    PROFESSIONS,
    REFERENCE_CONSUMPTION_RATE,
    REFERENCE_CORPORATE_RATE,
    REFERENCE_PERSONAL_RATE,
    LifeLevers,
    entrepreneur_gdp_factor,
    no_levers,
)
from backend.features.tax_policy import DEFAULT_TAX_POLICY
from tests.conftest import SetIndicator
from tests.fakes import monthly_series

START = date(2020, 1, 2)
SALARY = Decimal(5000)


def budget(
    profession: Profession,
    *,
    inflation_adjusted: bool = False,
    growth: str = "0.02",
    levers: LifeLevers | None = None,
) -> LifeBudget:
    life = LifeBudget(
        monthly_salary=SALARY,
        monthly_expense=Decimal(3000),
        withdrawal_rate=Decimal("0.04"),
        inflation_adjusted=inflation_adjusted,
        start_date=START,
        growth_on=lambda _day: Decimal(growth),
        levers_on=(lambda _day: levers) if levers else no_levers,
    )
    return life.for_profession(profession)


def test_reference_rates_match_the_default_tax_policy():
    assert DEFAULT_TAX_POLICY.personal_rate == REFERENCE_PERSONAL_RATE
    assert DEFAULT_TAX_POLICY.corporate_rate == REFERENCE_CORPORATE_RATE
    assert DEFAULT_TAX_POLICY.consumption_rate == REFERENCE_CONSUMPTION_RATE


@pytest.mark.parametrize(
    ("profession", "expected"),
    [
        (Profession.CLT, "5000"),
        (Profession.PUBLIC_SERVANT, "4500"),
        # PIB de 2%: o fator do empreendedor é 1
        (Profession.ENTREPRENEUR, "6000"),
        (Profession.RETIREE, "4250"),
        # Bico de 0,5x + auxílio de 0,4x no gasto de referência
        (Profession.WELFARE, "4500"),
        (Profession.LANDLORD, "5000"),
    ],
)
def test_each_profession_earns_its_multiple_of_the_host_salary(
    profession: Profession, expected: str
):
    assert budget(profession).net_salary_on(START) == Decimal(expected)


def test_public_servant_raise_follows_the_servants_measure(indicators: SetIndicator):
    # IPCA de ~12,68% no ano mais 3% de reajuste dos servidores
    indicators(IndicatorSeries.IPCA, monthly_series(date(2019, 1, 1), 36, "1"))
    ipca = Decimal("1.01") ** 12 - 1
    levers = LifeLevers(servant_raise=Decimal("0.03"))

    life = budget(Profession.PUBLIC_SERVANT, inflation_adjusted=True, levers=levers)

    assert life.salary_on(date(2021, 6, 1)) == (
        SALARY * Decimal("0.9") * (1 + ipca + Decimal("0.03"))
    ).quantize(Decimal("0.01"))


def test_entrepreneur_income_follows_the_gdp_with_a_floor():
    # PIB de -3,5%: fator de 1 + 3 x (-3,5% - 2%) = 0,835
    assert budget(Profession.ENTREPRENEUR, growth="-0.035").net_salary_on(
        START
    ) == Decimal("5010.00")
    assert entrepreneur_gdp_factor(Decimal("-0.5")) == Decimal("0.5")


def test_welfare_income_doubles_when_the_government_doubles_the_spending():
    levers = LifeLevers(welfare_spending=Decimal("0.03"))

    # Bico de 2.500 + auxílio de 2.000 x 2
    assert budget(Profession.WELFARE, levers=levers).net_salary_on(START) == Decimal(
        6500
    )


@pytest.mark.parametrize(
    ("profession", "expected"),
    [
        (Profession.CLT, "0"),
        (Profession.PUBLIC_SERVANT, "4500"),
        (Profession.ENTREPRENEUR, "6000"),
        (Profession.RETIREE, "4250"),
        # Só o auxílio sobra quando o bico se perde
        (Profession.WELFARE, "2000"),
        (Profession.LANDLORD, "0"),
    ],
)
def test_the_layoff_draw_takes_only_the_income_the_profession_is_exposed_to(
    profession: Profession, expected: str
):
    life = budget(profession)

    assert life.net_salary_on(START, income_lost=True) == Decimal(expected)


@pytest.mark.parametrize("profession", list(Profession))
def test_the_presidency_pays_three_salaries_whatever_the_profession(
    profession: Profession,
):
    life = budget(profession).as_president(Decimal(3))

    assert life.net_salary_on(START) == 3 * SALARY
    # O cargo não tem demissão, vaga nem perda de bico
    assert life.net_salary_on(START, income_lost=True) == 3 * SALARY
    assert life.income_loss() is None


def test_the_presidency_pays_nothing_when_the_match_salary_is_zero():
    life = replace(budget(Profession.CLT), monthly_salary=Decimal(0)).as_president(
        Decimal(3)
    )

    assert life.net_salary_on(START) == 0


def test_each_profession_loses_income_in_its_own_way():
    assert {p: PROFESSIONS[p].loss for p in Profession} == {
        Profession.CLT: IncomeLoss.LAYOFF,
        Profession.PUBLIC_SERVANT: None,
        Profession.ENTREPRENEUR: None,
        Profession.RETIREE: None,
        Profession.WELFARE: IncomeLoss.GIG_LOSS,
        Profession.LANDLORD: IncomeLoss.VACANCY,
    }


def test_only_the_retiree_pays_double_for_health():
    doubled = [p for p in Profession if PROFESSIONS[p].health_multiple == 2]

    assert doubled == [Profession.RETIREE]


def test_tax_deviation_cuts_the_income_of_the_profession_tax_only():
    levers = replace(no_levers(START), corporate_rate=Decimal("0.44"))

    # 10 pontos acima da lei no IR das empresas: só o empreendedor perde 10%
    assert budget(Profession.ENTREPRENEUR, levers=levers).net_salary_on(
        START
    ) == Decimal("5400.00")
    assert budget(Profession.CLT, levers=levers).net_salary_on(START) == SALARY
