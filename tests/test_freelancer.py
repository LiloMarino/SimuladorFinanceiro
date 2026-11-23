"""A tabela de preços do Autônomo: a curva de clientes e do mês vazio, a renda pelo preço, as recusas, a política dos bots e a leitura da página."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import cast

import pytest

from backend.core.dto.profession import SET_PRICE, FreelancerState, SetPrice
from backend.core.dto.profession_page import FreelancerMechanicDTO
from backend.core.enum import LifeHistoryKind, MechanicStatus, Profession
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.freelancer import (
    REFERENCE_EMPTY_MONTH,
    clients_on,
    curve_clients,
    empty_month_chance,
    empty_month_weight,
    price_range,
)
from backend.core.life_budget import LifeBudget
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.user_manager import UserManager
from backend.features.profession.freelancer import (
    next_price_change,
    policy_price,
    price_change_allowed,
    price_due,
    set_price,
)
from backend.features.simulation import simulation as simulation_module
from backend.features.strategy.bots import resolve_bot
from tests.test_bots import (  # noqa: F401
    person,
    professions_rules,
    refusal,
    room,
    started,
)
from tests.test_clt import turn_of_month
from tests.test_profession_mechanics import life_history, match
from tests.test_professions import SALARY, START, budget

DAY = date(2012, 3, 30)
NEUTRAL = Decimal(1)

pytestmark = pytest.mark.usefixtures("room")


def freelancer_page(sim, user) -> FreelancerMechanicDTO:
    """O bloco do Autônomo da página Profissão do jogador."""
    mechanic = sim.get_profession_page(user.client_id).mechanic
    assert isinstance(mechanic, FreelancerMechanicDTO)
    return mechanic


def freelancer_budget(
    *, deviation: str | None = None, unemployment: str = "1"
) -> LifeBudget:
    """O Autônomo com o preço `deviation` sobre a referência da partida e o desemprego `unemployment` vezes o neutro."""
    life = budget(Profession.FREELANCER)
    price = (
        None
        if deviation is None
        else life.reference_price_on(START) * (1 + Decimal(deviation))
    )
    return replace(
        life, unemployment_ratio_on=lambda _day: Decimal(unemployment)
    ).with_mechanic_state(lambda: FreelancerState(price=price))


def test_the_curve_hits_the_board_points():
    points = {"0": 34, "0.09": 32, "0.21": 27, "0.33": 21}

    for deviation, clients in points.items():
        assert curve_clients(Decimal(deviation)) == clients
    assert [empty_month_chance(Decimal(d)) for d in points] == [
        Decimal("0.02"),
        Decimal("0.03"),
        Decimal("0.06"),
        Decimal("0.11"),
    ]


def test_the_curve_is_linear_between_the_points_and_keeps_the_last_slope_after_them():
    # No meio do trecho de +9% a +21%: 29,5 clientes e 4,5% de mês vazio
    assert curve_clients(Decimal("0.15")) == Decimal("29.5")
    assert empty_month_chance(Decimal("0.15")) == Decimal("0.045")
    # O último trecho perde 6 clientes a cada 12 pontos: +45% tira 6 clientes a mais que +33%
    assert curve_clients(Decimal("0.45")) == Decimal(15)
    assert empty_month_chance(Decimal("0.5")) > Decimal("0.11")
    assert curve_clients(Decimal(2)) == 0


def test_below_the_reference_a_client_comes_for_each_four_percent_and_the_empty_month_stays():
    assert curve_clients(Decimal("-0.04")) == Decimal(35)
    assert curve_clients(Decimal("-0.2")) == Decimal(39)
    assert empty_month_chance(Decimal("-0.2")) == Decimal("0.02")
    assert empty_month_weight(Decimal("-0.2")) == 1
    assert empty_month_weight(Decimal("0.09")) == Decimal("1.5")


@pytest.mark.parametrize(
    ("ratio", "clients"),
    [
        # Desemprego no neutro: a curva
        ("1", "32"),
        # Dobro do neutro: a perda de 2 clientes dobra
        ("2", "30"),
        # Cinco vezes o neutro: o limite é 2x
        ("5", "30"),
        # Metade do neutro: a perda cai à metade
        ("0.5", "33"),
        # Desemprego quase nulo: o limite é 0,5x
        ("0.1", "33"),
    ],
)
def test_the_unemployment_multiplies_the_loss_of_clients_within_the_limits(
    ratio, clients
):
    assert clients_on(Decimal("0.09"), Decimal(ratio)) == Decimal(clients)


def test_the_unemployment_does_not_touch_the_clients_won_below_the_reference():
    assert clients_on(Decimal("-0.08"), Decimal(2)) == clients_on(
        Decimal("-0.08"), Decimal("0.5")
    )
    assert clients_on(Decimal(0), Decimal(2)) == 34


def test_the_price_range_is_from_minus_twenty_to_plus_fifty_percent_in_cents():
    assert price_range(Decimal(200)) == (Decimal("160.00"), Decimal("300.00"))
    assert price_range(Decimal("205.882352")) == (Decimal("164.71"), Decimal("308.82"))


def test_the_income_at_the_reference_price_is_the_base_income():
    life = freelancer_budget()

    assert life.price_on(START) == life.reference_price_on(START)
    assert life.clients_on(START) == 34
    assert life.salary_on(START) == SALARY * Decimal("1.4")


def test_a_higher_price_with_fewer_clients_changes_the_income_and_the_empty_month_weight():
    life = freelancer_budget(deviation="0.09")

    assert life.price_deviation_on(START) == Decimal("0.09")
    assert life.clients_on(START) == 32
    expected = life.reference_price_on(START) * Decimal("1.09") * 32
    assert abs(life.salary_on(START) - expected) <= Decimal("0.01")
    assert life.layoff_weight_on(START) == Decimal("1.5")
    assert freelancer_budget().layoff_weight_on(START) == 1


def test_a_higher_unemployment_costs_clients_only_above_the_reference():
    calm = freelancer_budget(deviation="0.21", unemployment="0.5")
    harsh = freelancer_budget(deviation="0.21", unemployment="2")

    assert calm.clients_on(START) == 30.5
    assert harsh.clients_on(START) == 20
    assert harsh.salary_on(START) < calm.salary_on(START)
    below = freelancer_budget(deviation="-0.1", unemployment="2")
    assert below.clients_on(START) == freelancer_budget(
        deviation="-0.1", unemployment="0.5"
    ).clients_on(START)


def test_the_price_range_of_the_budget_follows_the_reference_of_the_day():
    life = freelancer_budget()

    assert life.price_range_on(START) == price_range(life.reference_price_on(START))


def test_the_first_price_is_free_and_the_next_waits_for_the_next_month():
    first = set_price(
        FreelancerState(), SetPrice(price=Decimal("210"), reference=Decimal(200)), DAY
    )
    assert first.price == Decimal("210.00") and first.price_set_on == DAY
    assert next_price_change(first) == date(2012, 4, 1)
    assert not price_change_allowed(first, date(2012, 3, 31))
    assert price_change_allowed(first, date(2012, 4, 1))

    with pytest.raises(ConflictError, match="01/04/2012"):
        set_price(first, SetPrice(price=Decimal("220"), reference=Decimal(200)), DAY)
    later = set_price(
        first,
        SetPrice(price=Decimal("220"), reference=Decimal(200)),
        date(2012, 4, 2),
    )
    assert later.price == Decimal("220.00")


@pytest.mark.parametrize("price", ["159.99", "300.01"])
def test_the_price_out_of_the_range_is_refused(price):
    action = SetPrice(price=Decimal(price), reference=Decimal(200))

    with pytest.raises(ConflictError, match="R\\$ 160,00 a R\\$ 300,00"):
        set_price(FreelancerState(), action, DAY)


def test_the_range_limits_are_accepted():
    for price in ("160", "300"):
        action = SetPrice(price=Decimal(price), reference=Decimal(200))
        assert set_price(FreelancerState(), action, DAY).price == Decimal(price)


def test_the_bot_adjusts_once_a_year_since_the_last_adjustment_or_the_start():
    assert not price_due(FreelancerState(), date(2012, 1, 2), date(2012, 12, 31))
    assert price_due(FreelancerState(), date(2012, 1, 2), date(2013, 1, 2))
    adjusted = FreelancerState(price=Decimal(200), price_set_on=date(2012, 6, 1))
    assert not price_due(adjusted, date(2012, 1, 2), date(2013, 5, 31))
    assert price_due(adjusted, date(2012, 1, 2), date(2013, 6, 1))


def test_the_bot_repasses_the_inflation_and_adds_five_percent_with_the_unemployment_below_the_neutral():
    neutral = Decimal("0.09")
    ipca = Decimal("0.06")

    assert policy_price(Decimal(200), ipca, Decimal("0.07"), neutral) == Decimal(222)
    assert policy_price(Decimal(200), ipca, neutral, neutral) == Decimal(212)
    assert policy_price(Decimal(200), ipca, Decimal("0.12"), neutral) == Decimal(212)


def test_the_player_saves_the_price_and_the_history_records_the_action(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch, inflation_adjusted=True)
    sim.switch_profession(ana, Profession.FREELANCER)
    reference = freelancer_page(sim, ana).reference

    sim.set_price(ana, reference * Decimal("1.09"))

    state = sim.get_profession_state(ana.client_id).state
    assert isinstance(state, FreelancerState)
    assert state.price == (reference * Decimal("1.09")).quantize(Decimal("0.01"))
    assert state.price_set_on == sim.get_current_date()
    keys = [
        row.life_event_key
        for row in life_history(sim, ana.client_id)
        if row.kind is LifeHistoryKind.PROFESSION_ACTION
    ]
    assert keys == [SET_PRICE]


def test_the_player_price_is_refused_out_of_the_range_and_before_the_next_month(
    monkeypatch,
):
    ana = person("Ana")
    sim = match(monkeypatch, inflation_adjusted=True)
    sim.switch_profession(ana, Profession.FREELANCER)
    reference = freelancer_page(sim, ana).reference

    assert "20% abaixo a 50% acima" in refusal(
        lambda: sim.set_price(ana, reference * 2)
    )
    sim.set_price(ana, reference)
    assert "uma vez por mês" in refusal(lambda: sim.set_price(ana, reference))
    turn_of_month(sim)
    sim.set_price(ana, reference)


def test_only_the_freelancer_sets_the_price(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)

    assert "Autônomo" in refusal(lambda: sim.set_price(ana, Decimal(100)))


def test_the_page_reads_the_block_before_and_after_the_price_and_with_it_stalled(
    monkeypatch,
):
    ana = person("Ana")
    sim = match(monkeypatch, inflation_adjusted=True, end_date=date(2006, 12, 31))
    sim.switch_profession(ana, Profession.FREELANCER)

    start = sim.get_profession_page(ana.client_id).mechanic
    assert start.kind == "freelancer"
    assert start.status is MechanicStatus.AVAILABLE
    assert start.can_change_price and start.next_price_change is None
    assert [row.deviation for row in start.rows] == [
        Decimal(0),
        Decimal("0.09"),
        Decimal("0.21"),
        Decimal("0.33"),
    ]
    assert abs(start.rows[0].clients - 34) < Decimal("0.01")
    assert abs(start.month_income - start.price * start.clients) < 1

    sim.set_price(ana, start.reference * Decimal("1.09"))
    saved = sim.get_profession_page(ana.client_id).mechanic
    assert saved.kind == "freelancer"
    assert saved.status is MechanicStatus.ACTIVE
    assert not saved.can_change_price
    assert saved.next_price_change is not None
    assert abs(saved.clients - 32) < Decimal("0.01")
    assert not saved.stale

    # A linha do preço salvo rende o mesmo que o cartão "Renda do mês"
    saved_row = next(row for row in saved.rows if row.price == saved.price)
    assert saved_row.income == saved.month_income

    # A chance da tabela é a do sorteio: a da referência vezes o multiplicador que ele usa no dia
    user_id = UserManager.get_user_id(ana.client_id)
    budget = sim._life_budget(cast(LifeBudget, sim._life), user_id)
    draw = Decimal(str(sim._layoff_factor_for(budget)(sim._current_date)))
    assert abs(saved_row.empty_month_chance - REFERENCE_EMPTY_MONTH * draw) < Decimal(
        "0.0001"
    )

    for _ in range(12):
        turn_of_month(sim)
    parked = sim.get_profession_page(ana.client_id).mechanic
    assert parked.kind == "freelancer"
    assert parked.stalled_months == 12
    assert parked.reference_rise > 0
    assert parked.deviation < saved.deviation
    assert parked.can_change_price


def test_the_bot_adjusts_the_price_once_a_year_within_the_range(monkeypatch):
    changes = {"inflation_adjusted": True, "end_date": date(2006, 12, 31)}
    monkeypatch.setattr(SettingsManager, "_settings", professions_rules(**changes))
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.FREELANCER)
    )
    sim = match(monkeypatch, **changes)
    monkeypatch.setattr(
        simulation_module, "annual_index_rate", lambda series, day: Decimal("0.06")
    )

    for _ in range(11):
        turn_of_month(sim)
    state = sim.get_profession_state(bot.client_id).state
    assert isinstance(state, FreelancerState) and state.price is None

    for _ in range(2):
        turn_of_month(sim)
    adjusted = sim.get_profession_state(bot.client_id).state
    assert isinstance(adjusted, FreelancerState)
    assert adjusted.price is not None and adjusted.price_set_on is not None
    page = sim.get_profession_page(bot.client_id).mechanic
    assert page.kind == "freelancer"
    assert page.min_price <= adjusted.price <= page.max_price


def test_the_weight_of_a_price_table_row_is_the_weight_of_the_saved_price_at_that_deviation():
    saved = freelancer_budget(deviation="0.21")
    reference = freelancer_budget(deviation="0")

    assert saved.layoff_weight_on(START, Decimal("0.09")) == empty_month_weight(
        Decimal("0.09")
    )
    assert saved.layoff_weight_on(START) == reference.layoff_weight_on(
        START, Decimal("0.21")
    )
