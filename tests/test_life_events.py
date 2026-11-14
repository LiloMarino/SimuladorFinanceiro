from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.core.dto.life import (
    DEFAULT_LIFE_EVENTS,
    LifeEventTypeDTO,
    LifeFrequenciesDTO,
    validate_life_events,
)
from backend.core.enum import (
    IndicatorSeries,
    LifeEventEffect,
    LifeEventFamily,
    LifeFrequency,
    Profession,
)
from backend.core.life_budget import LifeBudget
from backend.core.life_events import LIFE_EVENT_CATALOG
from backend.core.professions import no_levers
from backend.core.utils import next_business_day
from backend.features.simulation.life_events import (
    layoff_factor_of,
    overdraft_interest,
    salary_skipped,
    unexpected_on,
)
from backend.features.simulation.simulation import Simulation
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


# Os três tipos que toda sala guarda, os únicos das salas salvas antes do catálogo ampliado
CLASSIC = tuple(
    e for e in DEFAULT_LIFE_EVENTS if e.key in ("REPAIR", "HEALTH", "LAYOFF")
)


def draws(seed: int, per_year: int, events=DEFAULT_LIFE_EVENTS) -> list:
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
        if (event := unexpected_on(3, day, 6, DEFAULT_LIFE_EVENTS))
        and event.key == "LAYOFF"
    )
    day = layoff[0]
    next_month = date(day.year + day.month // 12, day.month % 12 + 1, 1)

    assert salary_skipped(3, next_month, 6, START, DEFAULT_LIFE_EVENTS)


def test_a_month_without_layoff_pays_the_salary():
    assert not salary_skipped(3, date(2020, 2, 1), 0, START, DEFAULT_LIFE_EVENTS)


FINE = LifeEventTypeDTO(
    key="FINE",
    label="Multa",
    effect=LifeEventEffect.CASH_OUT,
    family=LifeEventFamily.EXPENSES,
    weight=1,
    expense_multiple=Decimal("0.5"),
    enabled=True,
)


def test_a_new_event_type_is_drawn_without_touching_the_engine():
    """A lista é a única fonte: um tipo novo, sozinho nela, é o único sorteado."""
    drawn = {e.key for e in draws(42, 6, (FINE,)) if e is not None}

    assert drawn == {FINE.key}


def test_a_disabled_type_is_never_drawn():
    types = [e.model_copy(update={"enabled": e.key != "HEALTH"}) for e in CLASSIC]

    drawn = {e.key for e in draws(42, 12, types) if e is not None}

    assert drawn == {"REPAIR", "LAYOFF"}


def test_a_custom_type_joins_the_draw_next_to_the_defaults():
    drawn = {e.key for e in draws(42, 12, (*CLASSIC, FINE)) if e is not None}

    assert drawn == {"REPAIR", "HEALTH", "LAYOFF", "FINE"}


def test_without_enabled_types_nothing_is_drawn():
    types = [e.model_copy(update={"enabled": False}) for e in DEFAULT_LIFE_EVENTS]

    assert all(e is None for e in draws(42, 12, types))


def test_the_frequency_holds_when_a_type_is_disabled():
    """Desligar um tipo troca quem sai, não quantos imprevistos saem por ano."""
    types = [
        e.model_copy(update={"enabled": e.key == "REPAIR"}) for e in DEFAULT_LIFE_EVENTS
    ]

    per_year = sum(e is not None for e in draws(42, 6, types)) / 20

    assert per_year == pytest.approx(6, rel=0.25)


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
        (
            event := unexpected_on(
                seed, day, 6, DEFAULT_LIFE_EVENTS, layoff_factor=factor
            )
        )
        is not None
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
    return [
        unexpected_on(seed, day, 6, DEFAULT_LIFE_EVENTS, layoff_factor=factor)
        for day in YEARS
    ]


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

    def net(rate: Decimal) -> Decimal:
        levers = replace(no_levers(START), personal_rate=rate)
        life = replace(
            budget(False), monthly_salary=Decimal(8000), levers_on=lambda _day: levers
        )
        return life.net_salary_on(START)

    assert net(reference) == Decimal(8000)
    # 5 pontos acima da referência descontam 5% do salário; abaixo, somam
    assert net(reference + Decimal("0.05")) == Decimal(7600)
    assert net(reference - Decimal("0.05")) == Decimal(8400)


def test_the_factory_types_may_be_edited_and_custom_ones_added():
    repair = DEFAULT_LIFE_EVENTS[0].model_copy(update={"expense_multiple": Decimal(2)})

    types = [repair, *DEFAULT_LIFE_EVENTS[1:], FINE]

    assert validate_life_events(types) == types


@pytest.mark.parametrize(
    "types",
    [
        [*DEFAULT_LIFE_EVENTS, DEFAULT_LIFE_EVENTS[0]],
        [e for e in DEFAULT_LIFE_EVENTS if e.key != "REPAIR"],
        [
            *CLASSIC[:2],
            CLASSIC[2].model_copy(update={"effect": LifeEventEffect.CASH_OUT}),
        ],
        [
            *DEFAULT_LIFE_EVENTS,
            *(FINE.model_copy(update={"key": f"X{n}"}) for n in range(40)),
        ],
    ],
    ids=["duplicate key", "factory type removed", "factory effect changed", "too many"],
)
def test_invalid_type_lists_are_rejected(types: list[LifeEventTypeDTO]):
    with pytest.raises(ValueError, match=r"única|removido|efeito|No máximo"):
        validate_life_events(types)


@pytest.mark.parametrize(
    "changes",
    [
        {"label": ""},
        {"expense_multiple": Decimal(-1)},
        {"expense_multiple": Decimal(25)},
        {"weight": 0},
    ],
)
def test_a_type_needs_a_label_a_sane_value_and_a_positive_weight(changes: dict):
    with pytest.raises(ValidationError):
        LifeEventTypeDTO.model_validate({**FINE.model_dump(), **changes})


SEEDS = range(10)


def draws_with(frequencies: LifeFrequenciesDTO) -> list:
    """Os sorteios de 20 anos em 10 salas (10 sementes), com a frequência pedida."""
    return [
        unexpected_on(seed, day, 60, DEFAULT_LIFE_EVENTS, frequencies=frequencies)
        for seed in SEEDS
        for day in YEARS
    ]


def family_counts(frequencies: LifeFrequenciesDTO) -> dict[LifeEventFamily, int]:
    counts = dict.fromkeys(LifeEventFamily, 0)
    for event in draws_with(frequencies):
        if event is not None:
            counts[event.family] += 1
    return counts


def test_the_catalog_has_at_least_twenty_types_and_one_in_four_is_good():
    good = sum(
        spec.weight
        for spec in LIFE_EVENT_CATALOG
        if spec.family is LifeEventFamily.GOOD
    )
    total = sum(spec.weight for spec in LIFE_EVENT_CATALOG)

    assert len(LIFE_EVENT_CATALOG) >= 20
    assert good * 4 == total


def test_with_everything_normal_between_22_and_28_percent_of_the_draws_are_good():
    sorted_events = [e for e in draws_with(LifeFrequenciesDTO()) if e is not None]
    good = sum(e.effect is LifeEventEffect.CASH_IN for e in sorted_events)

    assert len(sorted_events) >= 10000
    assert 0.22 <= good / len(sorted_events) <= 0.28


def test_a_family_set_to_off_is_never_drawn_and_the_others_keep_their_draws():
    normal = family_counts(LifeFrequenciesDTO())
    off = family_counts(LifeFrequenciesDTO(good=LifeFrequency.OFF))

    assert off[LifeEventFamily.GOOD] == 0
    assert off[LifeEventFamily.EXPENSES] == normal[LifeEventFamily.EXPENSES]
    income = LifeEventFamily.INCOME
    assert off[income] == pytest.approx(normal[income], rel=0.15)


def test_frequent_doubles_a_family_and_rare_halves_it_without_moving_the_others():
    normal = family_counts(LifeFrequenciesDTO())
    frequent = family_counts(LifeFrequenciesDTO(good=LifeFrequency.FREQUENT))
    rare = family_counts(LifeFrequenciesDTO(good=LifeFrequency.RARE))

    good = LifeEventFamily.GOOD
    assert frequent[good] == pytest.approx(2 * normal[good], rel=0.08)
    assert rare[good] == pytest.approx(normal[good] / 2, rel=0.08)
    expenses = LifeEventFamily.EXPENSES
    assert frequent[expenses] == pytest.approx(normal[expenses], rel=0.05)


def test_a_saved_room_with_the_three_original_types_still_validates():
    legacy = [
        {k: v for k, v in e.model_dump().items() if k != "family"} for e in CLASSIC
    ]

    types = validate_life_events([LifeEventTypeDTO.model_validate(e) for e in legacy])

    assert [e.family for e in types] == [
        LifeEventFamily.EXPENSES,
        LifeEventFamily.EXPENSES,
        LifeEventFamily.INCOME,
    ]


def layoff_days(seed: int, factor: float) -> set[date]:
    return {
        day
        for day in YEARS
        if (
            event := unexpected_on(
                seed, day, 6, DEFAULT_LIFE_EVENTS, layoff_factor=factor
            )
        )
        is not None
        and event.effect is LifeEventEffect.SKIP_NEXT_SALARY
    }


def test_a_heavier_layoff_weight_keeps_every_layoff_day_and_adds_others():
    """Com o mesmo número sorteado, quem pesa o dobro é demitido nos dias da sala e em outros."""
    room = layoff_days(42, 1.0)
    heavier = layoff_days(42, 2.0)

    assert room < heavier


def test_the_new_graduate_layoff_chance_is_the_room_chance_times_the_weight():
    class Room:
        _layoff_factor = staticmethod(lambda _day: 1.5)

    budget = LifeBudget(
        monthly_salary=Decimal(5000),
        monthly_expense=Decimal(3000),
        withdrawal_rate=Decimal("0.04"),
        inflation_adjusted=False,
        start_date=START,
        profession=Profession.NEW_GRADUATE,
    )
    clt = replace(budget, profession=Profession.CLT)

    factor_of = Simulation._layoff_factor_for
    assert factor_of(Room(), budget)(START) == pytest.approx(3.0)  # type: ignore[arg-type]
    assert factor_of(Room(), clt)(START) == pytest.approx(1.5)  # type: ignore[arg-type]
