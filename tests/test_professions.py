from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

import pytest

from backend.core.enum import IncomeLoss, IndicatorSeries, Profession
from backend.core.life_budget import LifeBudget
from backend.core.professions import (
    DRIVER_CURVES,
    NOMINAL_INHERITANCE_RATE,
    PROFESSIONS,
    REAL_INHERITANCE_RATE,
    REFERENCE_CONSUMPTION_RATE,
    REFERENCE_CORPORATE_RATE,
    REFERENCE_PERSONAL_RATE,
    IncomeDriver,
    LifeLevers,
    available_professions,
    driver_factor,
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
    dollar_change: str = "0",
    selic: str = "0.12",
    stocks: str = "0.12",
) -> LifeBudget:
    life = LifeBudget(
        monthly_salary=SALARY,
        monthly_expense=Decimal(3000),
        withdrawal_rate=Decimal("0.04"),
        inflation_adjusted=inflation_adjusted,
        start_date=START,
        growth_on=lambda _day: Decimal(growth),
        dollar_change_on=lambda _day: Decimal(dollar_change),
        selic_on=lambda _day: Decimal(selic),
        stocks_return_on=lambda _day: Decimal(stocks),
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
        # Aluguel de 1,1x o salário
        (Profession.LANDLORD, "5500"),
        # Com dólar, Selic e Ibovespa nos valores neutros o fator é 1
        (Profession.EXPORTER, "5250"),
        (Profession.BANKER, "5500"),
        (Profession.FREELANCER, "7000"),
        (Profession.BROKER, "5250"),
        # Vive do capital da herança: sem renda de trabalho
        (Profession.HEIR, "0"),
        # Começa em 0,6x e sobe com a carreira
        (Profession.NEW_GRADUATE, "3000"),
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
    assert driver_factor(DRIVER_CURVES[IncomeDriver.GDP], Decimal("-0.5")) == Decimal(
        "0.5"
    )


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
        (Profession.EXPORTER, "5250"),
        (Profession.BANKER, "0"),
        # O mês sem cliente tira toda a renda
        (Profession.FREELANCER, "0"),
        (Profession.BROKER, "5250"),
        (Profession.HEIR, "0"),
        (Profession.NEW_GRADUATE, "0"),
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
        Profession.EXPORTER: None,
        Profession.BANKER: IncomeLoss.LAYOFF,
        Profession.FREELANCER: IncomeLoss.NO_CLIENTS,
        Profession.BROKER: None,
        Profession.HEIR: None,
        Profession.NEW_GRADUATE: IncomeLoss.LAYOFF,
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


@pytest.mark.parametrize("driver", list(IncomeDriver))
def test_each_driver_curve_is_one_at_the_neutral_value(driver: IncomeDriver):
    curve = DRIVER_CURVES[driver]

    assert driver_factor(curve, curve.neutral) == 1


@pytest.mark.parametrize("driver", list(IncomeDriver))
def test_each_driver_curve_stops_at_its_floor(driver: IncomeDriver):
    curve = DRIVER_CURVES[driver]

    assert driver_factor(curve, Decimal(-10)) == curve.floor


@pytest.mark.parametrize(
    "driver", [d for d in IncomeDriver if DRIVER_CURVES[d].ceiling is not None]
)
def test_each_capped_driver_curve_stops_at_its_ceiling(driver: IncomeDriver):
    curve = DRIVER_CURVES[driver]

    assert driver_factor(curve, Decimal(10)) == curve.ceiling


def test_the_gdp_curve_has_no_ceiling():
    assert driver_factor(DRIVER_CURVES[IncomeDriver.GDP], Decimal("0.5")) > 2


@pytest.mark.parametrize(
    ("profession", "kwargs", "expected"),
    [
        # Dólar 20% acima em 12 meses: fator de 1,2 sobre 5.250
        (Profession.EXPORTER, {"dollar_change": "0.2"}, "6300"),
        # Selic de 16%: fator de 1 + 4 x (16% - 12%) = 1,16 sobre 5.500
        (Profession.BANKER, {"selic": "0.16"}, "6380"),
        # Ibovespa 20% abaixo: fator de 1 + 1,5 x (-20% - 12%) = 0,52 sobre 5.250
        (Profession.BROKER, {"stocks": "-0.2"}, "2730"),
    ],
)
def test_the_income_follows_the_variable_of_the_profession(
    profession: Profession, kwargs: dict[str, Any], expected: str
):
    assert budget(profession, **kwargs).net_salary_on(START) == Decimal(expected)


def test_the_freelancer_income_is_not_corrected_by_the_inflation(
    indicators: SetIndicator,
):
    indicators(IndicatorSeries.IPCA, monthly_series(date(2019, 1, 1), 48, "1"))
    later = date(2022, 6, 1)

    freelancer = budget(Profession.FREELANCER, inflation_adjusted=True)
    clt = budget(Profession.CLT, inflation_adjusted=True)

    assert freelancer.salary_on(later) == SALARY * Decimal("1.4")
    assert clt.salary_on(later) > SALARY


def test_the_new_graduate_career_rises_from_the_start_to_the_final_multiple():
    life = budget(Profession.NEW_GRADUATE)
    middle = START + timedelta(days=1826)
    end = START + timedelta(days=3653)

    assert life.multiple_on(START) == Decimal("0.6")
    assert abs(life.multiple_on(middle) - Decimal("1.05")) < Decimal("0.001")
    assert life.multiple_on(end) == Decimal("1.5")
    assert life.multiple_on(end + timedelta(days=3650)) == Decimal("1.5")


def test_the_new_graduate_layoff_weight_falls_to_one_in_ten_years():
    life = budget(Profession.NEW_GRADUATE)

    assert life.layoff_weight_on(START) == 2
    assert life.layoff_weight_on(START + timedelta(days=3653)) == 1
    assert budget(Profession.CLT).layoff_weight_on(START) == 1


def test_the_starting_capital_is_the_room_cash_except_for_the_heir_and_the_new_graduate():
    room = Decimal(10000)
    end = START + timedelta(days=3653)

    capitals = {p: budget(p).starting_capital(room, START, end) for p in Profession}

    assert capitals[Profession.NEW_GRADUATE] == 0
    assert capitals[Profession.HEIR] > room
    others = set(Profession) - {Profession.HEIR, Profession.NEW_GRADUATE}
    assert {capitals[p] for p in others} == {room}


@pytest.mark.parametrize(
    ("inflation_adjusted", "rate"),
    [(True, REAL_INHERITANCE_RATE), (False, NOMINAL_INHERITANCE_RATE)],
)
def test_the_inheritance_is_the_present_value_of_the_salaries_left_in_the_match(
    inflation_adjusted: bool, rate: Decimal
):
    room = Decimal(10000)
    one_year = START + timedelta(days=365)
    ten_years = START + timedelta(days=3653)
    heir = budget(Profession.HEIR, inflation_adjusted=inflation_adjusted)

    short = heir.starting_capital(room, START, one_year) - room
    long = heir.starting_capital(room, START, ten_years) - room
    late = heir.starting_capital(room, one_year, ten_years) - room

    # Um ano de salário trazido a valor presente: 12 x 5.000 / (1 + taxa)
    expected = SALARY * 12 / (1 + rate)
    assert abs(short - expected) < expected * Decimal("0.01")
    assert long > short
    # Quem entra com a partida rodando recebe só os anos que faltam
    assert short < late < long


def test_the_freelancer_exists_only_in_a_room_with_inflation_correction():
    assert Profession.FREELANCER in available_professions(True)
    assert Profession.FREELANCER not in available_professions(False)
    assert set(available_professions(False)) == set(Profession) - {
        Profession.FREELANCER
    }


def test_the_room_without_inflation_correction_discounts_the_inheritance_at_a_higher_rate():
    room = Decimal(10000)
    end = START + timedelta(days=3653)

    real = budget(Profession.HEIR, inflation_adjusted=True)
    nominal = budget(Profession.HEIR, inflation_adjusted=False)

    assert NOMINAL_INHERITANCE_RATE > REAL_INHERITANCE_RATE
    assert nominal.starting_capital(room, START, end) < real.starting_capital(
        room, START, end
    )
