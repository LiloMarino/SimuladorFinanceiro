"""Os imóveis do Locador: o preço pelo IVG-R, o aluguel e o reajuste pelo IGP-M, a vacância, a compra e a venda, o patrimônio travado, a política dos bots e a leitura da página."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core.clt import cents
from backend.core.dates import add_months
from backend.core.dto.profession import (
    PROPERTY_BOUGHT,
    PROPERTY_RENTED,
    PROPERTY_SOLD,
    PROPERTY_VACATED,
    LandlordState,
)
from backend.core.dto.profession_page import LandlordMechanicDTO
from backend.core.dto.real_estate import PropertyDTO
from backend.core.enum import (
    IncomeSeriesEffect,
    IncomeSeriesKey,
    IndicatorSeries,
    LockedAssetKind,
    MechanicStatus,
    Profession,
    PropertySize,
    PropertyStatus,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.indicators import annual_index_rate
from backend.core.life_budget import LifeBudget
from backend.core.locked_assets import LOCKED_EXITS, PROPERTY_COST_RATE
from backend.core.real_estate import (
    INITIAL_PROPERTIES,
    OFFER_SPREAD,
    PRICE_MULTIPLES,
    RENT_RATE,
    becomes_vacant,
    contract_rent_on,
    initial_drafts,
    next_readjustment,
    offers_of,
    price_factor,
    rent_of,
    rent_on,
    sale_proceeds,
    vacancy_chance,
    value_of,
)
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.economy.growth import NEUTRAL_UNEMPLOYMENT
from backend.features.profession.landlord import (
    policy_purchase,
    policy_sales,
)
from backend.features.profession.reserve import Reserve
from backend.features.simulation import simulation as simulation_module
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.strategy.bots import resolve_bot
from backend.routes.dependencies import get_client_id
from backend.routes.simulation import simulation_router
from tests.conftest import SetIndicator
from tests.fakes import monthly_series
from tests.test_bots import (  # noqa: F401
    person,
    professions_rules,
    refusal,
    room,
    started,
)
from tests.test_clt import RECESSION, turn_of_month, with_growth
from tests.test_profession_mechanics import life_history, match

pytestmark = pytest.mark.usefixtures("room")

DAY = date(2020, 1, 15)
SALARY = Decimal(3000)
MULTIPLE = Decimal("1.1")
FUNDS = Decimal(5_000_000)
NO_RESERVE = Reserve(cash=Decimal(0), health_cost=Decimal(0))


def property_of(
    *,
    id: int = 1,
    size: PropertySize = PropertySize.STUDIO,
    status: PropertyStatus = PropertyStatus.RENTED,
    base_price: str = "100000",
    contract_rent: str = "500",
    contract_start: date = DAY,
    offer_month: date | None = None,
    vacant_since: date | None = None,
    sale_due: date | None = None,
) -> PropertyDTO:
    return PropertyDTO(
        id=id,
        size=size,
        name="Imóvel",
        base_price=Decimal(base_price),
        offer_month=offer_month,
        contract_rent=Decimal(contract_rent),
        contract_start=contract_start,
        status=status,
        vacant_since=vacant_since,
        sale_due=sale_due,
    )


# --- O preço, o aluguel e o reajuste


def test_the_price_follows_the_property_index_month_by_month(indicators: SetIndicator):
    indicators(IndicatorSeries.IVG_R, monthly_series(DAY, 24, "1"))

    assert price_factor(DAY, DAY) == 1
    assert price_factor(DAY, date(2020, 4, 10)) == Decimal("1.01") ** 3
    assert price_factor(DAY, date(2021, 1, 15)) == pytest.approx(
        Decimal("1.01") ** 12, abs=Decimal("1e-9")
    )


def test_the_value_of_a_property_is_the_base_price_run_by_the_index(
    indicators: SetIndicator,
):
    indicators(IndicatorSeries.IVG_R, monthly_series(DAY, 24, "1"))
    item = property_of(base_price="100000")

    assert value_of(item, DAY, DAY) == Decimal(100000)
    assert value_of(item, DAY, date(2020, 3, 20)) == cents(
        Decimal(100000) * Decimal("1.01") ** 2
    )


def test_the_rent_is_readjusted_by_the_igpm_at_the_twelfth_contract_month(
    indicators: SetIndicator,
):
    indicators(IndicatorSeries.IGP_M, monthly_series(date(2019, 1, 1), 48, "1"))
    start = date(2020, 1, 10)

    before = contract_rent_on(Decimal(1000), start, date(2021, 1, 9))
    at = contract_rent_on(Decimal(1000), start, date(2021, 1, 10))
    second = contract_rent_on(Decimal(1000), start, date(2022, 1, 10))

    assert before == Decimal(1000)
    assert at == cents(Decimal(1000) * (Decimal("1.01") ** 12))
    assert second > at * Decimal("1.12")
    assert next_readjustment(start, date(2020, 6, 1)) == date(2021, 1, 10)
    assert next_readjustment(start, date(2021, 1, 10)) == date(2022, 1, 10)


def test_the_rent_is_half_a_percent_of_the_price():
    assert Decimal("0.005") == RENT_RATE
    assert rent_of(Decimal(200000)) == Decimal(1000)


def test_the_vacant_property_pays_nothing_and_the_selling_one_keeps_paying():
    vacant = property_of(status=PropertyStatus.VACANT, vacant_since=DAY)
    selling = property_of(status=PropertyStatus.SELLING, sale_due=DAY)

    assert rent_on(vacant, DAY) == 0
    assert rent_on(selling, DAY) == Decimal(500)


# --- Os imóveis iniciais


def test_the_initial_properties_are_three_with_rents_two_three_four():
    drafts = initial_drafts(SALARY, MULTIPLE, DAY, DAY)

    assert [(d.size, d.name) for d in drafts] == [
        (size, name) for size, name, _ in INITIAL_PROPERTIES
    ]
    assert [d.name for d in drafts] == [
        "Apartamento 1 quarto",
        "Apartamento 2 quartos",
        "Casa 3 quartos",
    ]
    rents = [d.contract_rent for d in drafts]
    assert sum(rents) == Decimal(3300)
    assert [round(r / rents[0] * 2) for r in rents] == [2, 3, 4]
    assert sum(d.base_price for d in drafts) == Decimal(660000)
    assert all(d.offer_month is None and d.contract_start == DAY for d in drafts)


def test_the_initial_properties_born_later_open_at_the_price_of_the_day(
    indicators: SetIndicator,
):
    indicators(IndicatorSeries.IVG_R, monthly_series(DAY, 24, "1"))
    later = date(2020, 7, 20)

    start_drafts = initial_drafts(SALARY, MULTIPLE, DAY, DAY)
    drafts = initial_drafts(SALARY, MULTIPLE, DAY, later)

    for born, original in zip(drafts, start_drafts, strict=True):
        assert born.base_price == original.base_price
        assert born.contract_start == later
        assert born.contract_rent == rent_of(born.base_price * price_factor(DAY, later))
        assert born.contract_rent > original.contract_rent


# --- A vacância


def test_the_vacancy_chance_with_neutral_unemployment_is_five_percent():
    assert vacancy_chance(Decimal(1), Decimal(0)) == Decimal("0.05")


def test_the_vacancy_chance_scales_by_unemployment_and_adds_a_point_per_gdp_point_lost():
    # 10,8% de desemprego sobre o neutro de 9% (1,2) e PIB de -1%: 5% x 1,2 + 1 ponto
    chance = vacancy_chance(Decimal("0.108") / Decimal("0.09"), Decimal("-0.01"))

    assert chance == Decimal("0.07")


def test_the_vacancy_chance_stays_between_two_and_twenty_percent():
    assert vacancy_chance(Decimal("0.1"), Decimal(0)) == Decimal("0.02")
    assert vacancy_chance(Decimal(10), Decimal("-0.3")) == Decimal("0.20")


def test_a_positive_gdp_does_not_change_the_vacancy_chance():
    base = vacancy_chance(Decimal("1.2"), Decimal(0))

    assert vacancy_chance(Decimal("1.2"), Decimal("0.05")) == base


def test_the_vacancy_draw_is_stable_and_follows_the_chance():
    month = date(2020, 2, 1)

    assert becomes_vacant(7, 1, month, 3, Decimal(1))
    assert not becomes_vacant(7, 1, month, 3, Decimal(0))
    again = [becomes_vacant(7, 1, month, 3, Decimal("0.5")) for _ in range(3)]
    assert len(set(again)) == 1
    drawn = sum(
        becomes_vacant(7, 1, add_months(month, i), 3, Decimal("0.2"))
        for i in range(400)
    )
    assert 40 < drawn < 120


# --- As ofertas


def test_the_offers_are_one_per_size_within_ten_percent_of_the_price_of_the_day():
    offers = offers_of(5, date(2020, 2, 1), SALARY, DAY, DAY)

    assert [o.size for o in offers] == list(PRICE_MULTIPLES)
    for offer in offers:
        today = SALARY * PRICE_MULTIPLES[offer.size]
        assert today * (1 - OFFER_SPREAD) <= offer.price <= today * (1 + OFFER_SPREAD)
        assert offer.rent == rent_of(offer.price)
        assert offer.cost == cents(offer.price * PROPERTY_COST_RATE)
    assert offers == offers_of(5, date(2020, 2, 1), SALARY, DAY, DAY)
    assert offers != offers_of(5, date(2020, 3, 1), SALARY, DAY, DAY)


# --- A política do bot


def test_the_bot_buys_the_biggest_offer_it_can_pay_when_the_cdi_is_low():
    offers = offers_of(5, date(2020, 2, 1), SALARY, DAY, DAY)
    cash = Decimal(10_000_000)

    chosen = policy_purchase(offers, set(), Decimal("0.03"), cash, NO_RESERVE)

    assert chosen is not None and chosen.size is PropertySize.HOUSE
    smaller = policy_purchase(
        offers, {PropertySize.HOUSE}, Decimal("0.03"), cash, NO_RESERVE
    )
    assert smaller is not None and smaller.size is PropertySize.TWO_BEDROOM


def test_the_bot_does_not_buy_when_the_cdi_beats_the_rent_or_the_cash_falls_short():
    offers = offers_of(5, date(2020, 2, 1), SALARY, DAY, DAY)

    assert (
        policy_purchase(offers, set(), Decimal("0.12"), Decimal(10**8), NO_RESERVE)
        is None
    )
    assert (
        policy_purchase(offers, set(), Decimal("0.03"), Decimal(1000), NO_RESERVE)
        is None
    )


def test_the_bot_keeps_the_health_reserve_when_it_buys():
    [studio, *_] = offers_of(5, date(2020, 2, 1), SALARY, DAY, DAY)
    reserve = Reserve(cash=Decimal(0), health_cost=Decimal(5000))
    cash = studio.price + studio.cost + Decimal(4000)

    assert policy_purchase([studio], set(), Decimal("0.03"), cash, reserve) is None
    assert (
        policy_purchase([studio], set(), Decimal("0.03"), cash + 1000, reserve)
        is studio
    )


def test_the_bot_sells_the_property_that_yields_below_the_cdi_by_five_points():
    # Aluguel de 6% ao ano sobre o valor
    items = [property_of(id=1), property_of(id=2, status=PropertyStatus.VACANT)]

    assert policy_sales(items, DAY, DAY, Decimal("0.12")) == [1]
    assert policy_sales(items, DAY, DAY, Decimal("0.10")) == []


# --- A partida


def landlord_match(monkeypatch, *names: str):
    """A partida com um jogador de Locador por nome; o valor dos imóveis passa da meta de viver de renda, que aqui não encerra a partida."""
    users = [person(name) for name in names]
    monkeypatch.setattr(simulation_module, "goal_reached", lambda *args: False)
    sim = match(monkeypatch)
    for user in users:
        sim.switch_profession(user, Profession.LANDLORD)
        page_of(sim, user)
    return sim, *users


def new_landlord(monkeypatch):
    """A partida com a Ana de Locadora e os imóveis iniciais já nascidos, com caixa para comprar."""
    sim, ana = landlord_match(monkeypatch, "Ana")
    fund(sim, ana)
    return sim, ana


def fund(sim, user, amount: Decimal = FUNDS) -> None:
    """Soma `amount` ao caixa do jogador."""
    sim._engine.record_profession_action(user.client_id, "test_funds", amount)


def page_of(sim, user) -> LandlordMechanicDTO:
    mechanic = sim.get_profession_page(user.client_id).mechanic
    assert isinstance(mechanic, LandlordMechanicDTO)
    return mechanic


def budget_of(sim, user) -> LifeBudget:
    assert sim._life is not None
    return sim._life_budget(sim._life, user.id)


def properties_of(sim, user) -> list[PropertyDTO]:
    return sim._property_book.of(user.id)


def actions_of(sim, user, key: str):
    return [r for r in life_history(sim, user.client_id) if r.life_event_key == key]


def test_the_landlord_starts_with_three_rented_properties_that_pay_one_point_one_salaries(
    monkeypatch,
):
    sim, ana = new_landlord(monkeypatch)
    salary = sim._life.monthly_salary if sim._life else Decimal(0)

    items = properties_of(sim, ana)

    assert [i.name for i in items] == [
        "Apartamento 1 quarto",
        "Apartamento 2 quartos",
        "Casa 3 quartos",
    ]
    assert all(i.status is PropertyStatus.RENTED for i in items)
    day = sim.get_current_date()
    income = sim._rented_income_on(ana.id, day)
    assert abs(income - salary * MULTIPLE) <= Decimal("0.02")
    block = page_of(sim, ana)
    assert block.status is MechanicStatus.ACTIVE
    assert (block.rented, block.total) == (3, 3)
    assert block.income == income
    assert abs(block.total_value - salary * MULTIPLE / RENT_RATE) <= Decimal(1)


def test_the_income_is_the_sum_of_the_rented_properties_and_zero_without_them(
    monkeypatch,
):
    sim, ana = new_landlord(monkeypatch)
    day = sim.get_current_date()
    first, second, third = properties_of(sim, ana)
    full = sim._rented_income_on(ana.id, day)

    sim._property_book.vacate(ana.id, first.id, day)

    assert sim._rented_income_on(ana.id, day) == full - first.contract_rent
    assert page_of(sim, ana).income == full - first.contract_rent
    sim._property_book.vacate(ana.id, second.id, day)
    sim._property_book.vacate(ana.id, third.id, day)
    assert sim._rented_income_on(ana.id, day) == 0
    assert page_of(sim, ana).income == 0
    budget = budget_of(sim, ana)
    assert budget.net_salary_on(day) == 0


def test_the_landlord_has_no_layoff_draw(monkeypatch):
    sim, ana = new_landlord(monkeypatch)

    budget = budget_of(sim, ana)

    assert budget.income_loss() is None
    assert budget.net_salary_on(
        sim.get_current_date(), income_lost=True
    ) == budget.net_salary_on(sim.get_current_date())


def test_the_landlord_page_shows_the_series_that_move_the_rent_with_the_effect_of_today(
    monkeypatch,
):
    sim, ana = new_landlord(monkeypatch)
    with_growth(sim, monkeypatch, RECESSION)
    day = sim.get_current_date()

    page = sim.get_profession_page(ana.client_id)
    by_key = {item.key: item for item in page.series}
    macro = sim._macro.latest(day)
    expected = vacancy_chance(macro.unemployment / NEUTRAL_UNEMPLOYMENT, macro.growth)

    assert list(by_key) == [
        IncomeSeriesKey.GDP,
        IncomeSeriesKey.UNEMPLOYMENT,
        IncomeSeriesKey.IGP_M,
    ]
    for key in (IncomeSeriesKey.GDP, IncomeSeriesKey.UNEMPLOYMENT):
        assert by_key[key].effect == expected
        assert by_key[key].effect_kind is IncomeSeriesEffect.VACANCY_CHANCE
        assert len(by_key[key].points) == 12
    assert by_key[IncomeSeriesKey.GDP].neutral is not None
    assert by_key[IncomeSeriesKey.UNEMPLOYMENT].neutral == NEUTRAL_UNEMPLOYMENT
    igpm = by_key[IncomeSeriesKey.IGP_M]
    assert igpm.effect == igpm.current == annual_index_rate(IndicatorSeries.IGP_M, day)
    assert igpm.effect_kind is IncomeSeriesEffect.RENT_ADJUSTMENT
    assert len(igpm.points) == 12


def test_the_properties_are_read_back_from_the_database_without_new_ones(monkeypatch):
    sim, ana = new_landlord(monkeypatch)
    before = properties_of(sim, ana)

    sim._property_book.forget()

    assert properties_of(sim, ana) == before
    assert len(page_of(sim, ana).properties) == 3


def test_a_saved_game_with_a_landlord_and_no_properties_gets_the_initial_ones(
    monkeypatch,
):
    sim, ana = new_landlord(monkeypatch)
    sim._property_book.clear(ana.id)
    sim._profession_book.save_state(ana.id, LandlordState())

    block = page_of(sim, ana)

    assert block.total == 3
    assert all(row.status is PropertyStatus.RENTED for row in block.properties)
    state = sim._profession_book.state_of(ana.id, Profession.LANDLORD)
    assert isinstance(state, LandlordState) and state.seeded


def test_who_sold_everything_does_not_get_the_initial_ones_again(monkeypatch):
    sim, ana = new_landlord(monkeypatch)
    sim._property_book.clear(ana.id)

    assert page_of(sim, ana).total == 0


# --- A virada do mês: vacância e volta ao aluguel


def test_the_month_turn_vacates_the_property_and_the_next_turn_rents_it_again_at_the_price_of_the_day(
    monkeypatch,
):
    sim, ana = new_landlord(monkeypatch)
    monkeypatch.setattr(simulation_module, "becomes_vacant", lambda *a: True)
    monkeypatch.setattr(simulation_module, "is_rented_again", lambda *a: False)

    turn_of_month(sim)

    items = properties_of(sim, ana)
    assert all(i.status is PropertyStatus.VACANT for i in items)
    assert len(actions_of(sim, ana, PROPERTY_VACATED)) == 3
    assert page_of(sim, ana).income == 0
    monkeypatch.setattr(simulation_module, "is_rented_again", lambda *a: True)

    day = turn_of_month(sim)

    start = sim.settings.start_date
    for item in properties_of(sim, ana):
        assert item.status is PropertyStatus.RENTED
        assert item.contract_start == day
        assert item.contract_rent == rent_of(value_of(item, start, day))
    assert len(actions_of(sim, ana, PROPERTY_RENTED)) == 3


def test_a_contract_signed_in_the_month_does_not_draw_vacancy(monkeypatch):
    sim, ana = new_landlord(monkeypatch)
    day = sim.get_current_date()
    monkeypatch.setattr(simulation_module, "becomes_vacant", lambda *a: True)

    sim._run_landlord_month([ana], day)

    assert all(i.status is PropertyStatus.RENTED for i in properties_of(sim, ana))


# --- A compra


def test_the_purchase_takes_the_price_plus_five_percent_and_the_property_enters_rented(
    monkeypatch,
):
    sim, ana = new_landlord(monkeypatch)
    block = page_of(sim, ana)
    offer = next(o for o in block.offers if o.size is PropertySize.STUDIO)
    cash = sim.get_cash(ana.client_id)
    day = sim.get_current_date()

    sim.buy_property(ana, PropertySize.STUDIO)

    assert offer.cost == cents(offer.price * Decimal("0.05"))
    assert sim.get_cash(ana.client_id) == cash - offer.price - offer.cost
    bought = properties_of(sim, ana)[-1]
    assert bought.name == "Kitnet"
    assert bought.status is PropertyStatus.RENTED
    assert bought.contract_start == day
    assert bought.contract_rent == rent_of(offer.price)
    assert value_of(bought, sim.settings.start_date, day) == offer.price
    [row] = actions_of(sim, ana, PROPERTY_BOUGHT)
    assert row.amount == -(offer.price + offer.cost)
    assert row.cash_after == sim.get_cash(ana.client_id)
    assert next(
        o for o in page_of(sim, ana).offers if o.size is PropertySize.STUDIO
    ).bought


def test_each_offer_is_bought_once_a_month(monkeypatch):
    sim, ana = new_landlord(monkeypatch)
    sim.buy_property(ana, PropertySize.STUDIO)

    message = refusal(lambda: sim.buy_property(ana, PropertySize.STUDIO))

    assert "já comprou" in message
    sim.buy_property(ana, PropertySize.TWO_BEDROOM)
    assert len(properties_of(sim, ana)) == 5


def test_the_purchase_is_refused_without_cash_for_the_price_and_the_cost(monkeypatch):
    sim, ana = new_landlord(monkeypatch)
    cash = sim.get_cash(ana.client_id)
    fund(sim, ana, -cash + 1000)

    message = refusal(lambda: sim.buy_property(ana, PropertySize.HOUSE))

    assert "Caixa insuficiente" in message
    assert len(properties_of(sim, ana)) == 3


def test_only_the_landlord_buys_and_sells(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim.switch_profession(ana, Profession.PUBLIC_SERVANT)

    with pytest.raises(ConflictError):
        sim.buy_property(ana, PropertySize.STUDIO)
    with pytest.raises(ConflictError):
        sim.sell_property(ana, 1)


# --- A venda


def test_the_sale_concludes_one_month_later_at_the_price_of_that_day_minus_five_percent(
    monkeypatch,
):
    sim, ana = new_landlord(monkeypatch)
    day = sim.get_current_date()
    item = properties_of(sim, ana)[0]
    rent = sim._rented_income_on(ana.id, day)

    sim.sell_property(ana, item.id)

    selling = properties_of(sim, ana)[0]
    due = selling.sale_due
    assert due is not None
    assert selling.status is PropertyStatus.SELLING
    assert due == add_months(day, 1)
    assert sim._rented_income_on(ana.id, day) == rent
    row = next(r for r in page_of(sim, ana).properties if r.id == item.id)
    assert row.sale_due == due
    calls: list[tuple[str, Decimal]] = []
    monkeypatch.setattr(
        sim._engine,
        "record_profession_action",
        lambda client_id, kind, payout=Decimal(0): calls.append((kind, payout)),
    )

    sim._conclude_property_sales([ana], due - timedelta(days=1))
    assert calls == [] and len(properties_of(sim, ana)) == 3
    sim._conclude_property_sales([ana], due)

    start = sim.settings.start_date
    assert calls == [(PROPERTY_SOLD, sale_proceeds(value_of(item, start, due)))]
    assert len(properties_of(sim, ana)) == 2
    assert all(i.id != item.id for i in properties_of(sim, ana))


def test_the_sale_cannot_be_asked_twice_or_for_a_stranger_property(monkeypatch):
    sim, ana = new_landlord(monkeypatch)
    item = properties_of(sim, ana)[0]
    sim.sell_property(ana, item.id)

    assert "já está à venda" in refusal(lambda: sim.sell_property(ana, item.id))
    assert "não está na sua carteira" in refusal(
        lambda: sim.sell_property(ana, 999_999), 404
    )


def test_the_sale_reaches_the_cash_when_the_match_runs(monkeypatch):
    sim, ana = new_landlord(monkeypatch)
    item = properties_of(sim, ana)[0]
    sim.sell_property(ana, item.id)
    due = add_months(sim.get_current_date(), 1)

    while sim.get_current_date() < due:
        sim.next_tick()

    assert all(i.id != item.id for i in properties_of(sim, ana))
    assert len(actions_of(sim, ana, PROPERTY_SOLD)) == 1


# --- O patrimônio travado e a troca de profissão


def test_the_properties_are_a_locked_asset_in_the_networth(monkeypatch):
    sim, ana = new_landlord(monkeypatch)
    day, start = sim.get_current_date(), sim.settings.start_date
    value = sum((value_of(i, start, day) for i in properties_of(sim, ana)), Decimal(0))
    cash_only = sim.get_cash(ana.client_id)

    portfolio = sim.get_portfolio(ana.client_id)

    [asset] = portfolio.locked_assets
    assert asset.kind is LockedAssetKind.REAL_ESTATE
    assert asset.value == value
    assert asset.exit_rule == LOCKED_EXITS[LockedAssetKind.REAL_ESTATE].rule
    assert asset.note == (
        "3 imóveis pelo preço do IVG-R · vender leva até 1 mês e custa 5%"
    )
    assert portfolio.locked_value == value
    assert portfolio.total_networth >= cash_only + value


def test_the_switch_sells_every_property_at_once_with_the_five_percent_cost(
    monkeypatch,
):
    sim, ana = new_landlord(monkeypatch)
    day, start = sim.get_current_date(), sim.settings.start_date
    value = sum((value_of(i, start, day) for i in properties_of(sim, ana)), Decimal(0))
    cash = sim.get_cash(ana.client_id)

    sim.switch_profession(ana, Profession.PUBLIC_SERVANT)

    assert sim.get_cash(ana.client_id) == cash + value * Decimal("0.95")
    assert properties_of(sim, ana) == []
    assert sim.get_portfolio(ana.client_id).locked_value == 0


# --- A política do bot na partida


def landlord_bot(monkeypatch, cdi: str):
    """A partida com um bot Locador e o CDI fixo em `cdi` ao ano."""
    person("Ana")
    real = simulation_module.annual_index_rate
    monkeypatch.setattr(
        simulation_module,
        "annual_index_rate",
        lambda series, day: (
            Decimal(cdi) if series is IndicatorSeries.CDI else real(series, day)
        ),
    )
    monkeypatch.setattr(simulation_module, "goal_reached", lambda *args: False)
    settings = professions_rules(unexpected_per_year=0)
    monkeypatch.setattr(SettingsManager, "_settings", settings)
    bot = UserManager.add_bot(
        "Rentista", resolve_bot("cdi_100", {}, profession=Profession.LANDLORD)
    )
    SimulationLoader.create(settings)
    sim = SimulationManager.get_active_simulation()
    page_of(sim, bot)
    return sim, bot


def test_the_bot_buys_with_a_low_cdi(monkeypatch):
    sim, bot = landlord_bot(monkeypatch, "0.03")
    fund(sim, bot)

    sim._run_landlord_policy(bot, sim.get_current_date(), NO_RESERVE)

    assert len(properties_of(sim, bot)) == 4
    assert properties_of(sim, bot)[-1].offer_month is not None


def test_the_bot_sells_with_a_high_cdi(monkeypatch):
    sim, bot = landlord_bot(monkeypatch, "0.20")

    turn_of_month(sim)

    assert [i.status for i in properties_of(sim, bot)] == [PropertyStatus.SELLING] * 3


# --- A página e as rotas


def test_the_page_reads_the_block_with_the_rows_and_the_offers(monkeypatch):
    sim, ana = new_landlord(monkeypatch)
    day, start = sim.get_current_date(), sim.settings.start_date

    block = page_of(sim, ana)

    assert [row.name for row in block.properties] == [
        i.name for i in properties_of(sim, ana)
    ]
    for row, item in zip(block.properties, properties_of(sim, ana), strict=True):
        assert row.value == value_of(item, start, day)
        assert row.next_readjustment == next_readjustment(item.contract_start, day)
    assert [o.size for o in block.offers] == list(PRICE_MULTIPLES)
    assert block.offers_month == day.replace(day=1)
    assert block.rent_rate == RENT_RATE and block.cost_rate == PROPERTY_COST_RATE
    assert block.sale_months == 1
    assert block.annual_yield == block.full_yield


def test_the_offers_are_the_same_for_every_landlord_in_the_room(monkeypatch):
    sim, ana, bruno = landlord_match(monkeypatch, "Ana", "Bruno")

    assert page_of(sim, ana).offers == page_of(sim, bruno).offers


def test_the_routes_buy_and_sell(monkeypatch):
    sim, ana = new_landlord(monkeypatch)
    app = FastAPI()
    app.include_router(simulation_router)
    app.dependency_overrides[get_client_id] = lambda: ana.client_id
    client = TestClient(app)
    item = properties_of(sim, ana)[0]

    buy = client.post("/api/simulation/buy-property", json={"size": "HOUSE"})
    again = client.post("/api/simulation/buy-property", json={"size": "HOUSE"})
    sell = client.post("/api/simulation/sell-property", json={"property_id": item.id})
    sell_again = client.post(
        "/api/simulation/sell-property", json={"property_id": item.id}
    )

    assert buy.status_code == 200
    assert again.status_code == 409
    assert sell.status_code == 200
    assert sell_again.status_code == 409
    assert len(properties_of(sim, ana)) == 4
