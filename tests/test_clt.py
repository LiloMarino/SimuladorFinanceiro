"""A mecânica do CLT: o FGTS (depósito, rendimento, saque na demissão, patrimônio) e a hora extra."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.clt import (
    FGTS_ANNUAL_RATE,
    fgts_deposit,
    fgts_payout,
    fgts_yield,
)
from backend.core.dto.life import DEFAULT_LIFE_EVENTS
from backend.core.dto.profession import (
    OVERTIME_ENDED,
    OVERTIME_OFF,
    OVERTIME_ON,
    CltState,
    MechanicState,
    SetOvertime,
)
from backend.core.enum import (
    CashflowEventType,
    FixedIncomeType,
    IndicatorSeries,
    LifeHistoryCategory,
    LifeHistoryKind,
    Profession,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.life_budget import LifeBudget
from backend.core.networth import networth
from backend.core.rates import Percent
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.profession.clt import (
    after_layoff,
    after_month,
    overtime_ends_with_recession,
    overtime_policy,
    set_overtime,
)
from backend.features.profession.mechanics import apply_action
from backend.features.profession.profession_book import ProfessionBook
from backend.features.profession.reserve import Reserve
from backend.features.simulation import simulation as simulation_module
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.strategy.bots import resolve_bot
from backend.features.strategy.cdi import CdiReference
from backend.routes.dependencies import get_client_id
from backend.routes.simulation import simulation_router
from tests.fakes import macro_month, simulation_settings
from tests.test_bots import (  # noqa: F401
    person,
    refusal,
    room,
    rules,
    started,
)
from tests.test_profession_mechanics import life_history, match

DAY = date(2004, 3, 29)
GROWING = macro_month("0.03")
STAGNANT = macro_month("0.02")
RECESSION = macro_month("-0.01")
ZERO_GROWTH = macro_month("0")
# O caixa de quem cobre o imprevisto de saúde em dobro: 4 despesas mensais de 5.000
COVERED = Reserve(cash=Decimal(20000), health_cost=Decimal(10000))
# Caixa de partida folgado: o bot cobre o imprevisto de saúde em dobro
RICH = Decimal(100000)
BROKE = Reserve(cash=Decimal(19999), health_cost=Decimal(10000))

pytestmark = pytest.mark.usefixtures("room")


def layoff_event():
    return next(e for e in DEFAULT_LIFE_EVENTS if e.key == "LAYOFF")


def turn_of_month(sim: Simulation) -> date:
    """Avança até o 1º pregão do mês seguinte e devolve o dia."""
    month = sim.get_current_date().month
    for _ in range(40):
        sim.next_tick()
        if sim.get_current_date().month != month:
            return sim.get_current_date()
    raise AssertionError("O mês não virou")


def mid_month(sim: Simulation) -> None:
    """Avança até um dia do meio do mês, em que o próximo pregão ainda é do mesmo mês."""
    while sim.get_current_date().day < 10:
        sim.next_tick()


def state_of(sim: Simulation, user) -> CltState:
    state = sim.get_profession_state(user.client_id).state
    assert isinstance(state, CltState)
    return state


def with_tr(monkeypatch: pytest.MonkeyPatch, value: str | None) -> None:
    """A TR do mês, em % ao mês, que a partida lê; sem valor, a série não existe."""
    monkeypatch.setattr(
        simulation_module,
        "last_known_rate",
        lambda series, day: (
            Percent(Decimal(value))
            if series is IndicatorSeries.TR and value is not None
            else None
        ),
    )


def with_growth(sim: Simulation, monkeypatch: pytest.MonkeyPatch, macro) -> None:
    """A economia do mês que a partida vê: o PIB de 12 meses do `macro`."""
    real = sim._macro.latest
    monkeypatch.setattr(
        sim._macro,
        "latest",
        lambda day: replace(real(day), growth=macro.growth),
    )


def with_layoff_on_demand(monkeypatch: pytest.MonkeyPatch) -> dict[str, bool]:
    """A demissão sorteada: sai no pregão em que a chave está ligada, e só nele."""
    switch = {"on": False}
    monkeypatch.setattr(
        simulation_module,
        "unexpected_on",
        lambda seed, day, *args, **kwargs: layoff_event() if switch["on"] else None,
    )
    monkeypatch.setattr(
        simulation_module, "salary_skipped", lambda *args, **kwargs: False
    )
    return switch


def test_the_deposit_is_eight_percent_of_the_gross():
    assert fgts_deposit(Decimal(8000)) == Decimal("640.00")
    assert fgts_deposit(Decimal(10000)) == Decimal("800.00")


def test_the_yield_is_three_percent_a_year_in_a_month_with_the_tr_on_top():
    balance = Decimal(10000)

    assert fgts_yield(balance, Decimal(0)) == Decimal("24.66")
    monthly = (1 + FGTS_ANNUAL_RATE) ** (Decimal(1) / 12) * (1 + Decimal("0.005")) - 1
    assert fgts_yield(balance, Decimal("0.005")) == (balance * monthly).quantize(
        Decimal("0.01")
    )


def test_the_payout_is_the_balance_plus_forty_percent():
    assert fgts_payout(Decimal(10000)) == Decimal("14000.00")
    assert fgts_payout(Decimal(0)) == Decimal("0.00")


def test_a_paid_month_yields_and_deposits_and_a_month_without_pay_only_yields():
    state = CltState(fgts_balance=Decimal(10000))

    paid = after_month(state, Decimal(8000), Decimal(0), salary_paid=True)
    unpaid = after_month(state, Decimal(8000), Decimal(0), salary_paid=False)

    assert paid.fgts_balance == Decimal("10664.66")
    assert unpaid.fgts_balance == Decimal("10024.66")


def test_the_layoff_empties_the_account_and_turns_the_overtime_off():
    state = CltState(fgts_balance=Decimal(10000), overtime=True)

    reset, payout = after_layoff(state)

    assert reset == CltState(fgts_balance=Decimal(0), overtime=False)
    assert payout == Decimal("14000.00")


def test_the_overtime_raises_the_income_by_a_quarter_and_doubles_the_health_cost():
    budget = LifeBudget.of(simulation_settings()).for_profession(Profession.CLT)
    day = DAY
    base = budget.salary_on(day)

    on = budget.with_mechanic_state(lambda: CltState(overtime=True))
    off = budget.with_mechanic_state(lambda: CltState())

    assert on.salary_on(day) == base * Decimal("1.25")
    assert off.salary_on(day) == base
    assert on.health_multiple == 2 * off.health_multiple


def test_the_overtime_is_refused_with_a_negative_gdp_and_allowed_from_zero():
    state = CltState()
    on = SetOvertime(kind=OVERTIME_ON)

    with pytest.raises(ConflictError, match="PIB"):
        set_overtime(state, on, DAY, RECESSION)

    assert set_overtime(state, on, DAY, ZERO_GROWTH).overtime is True


def test_turning_the_overtime_off_is_allowed_in_a_recession():
    state = CltState(overtime=True)

    off = set_overtime(state, SetOvertime(kind=OVERTIME_OFF), DAY, RECESSION)

    assert off.overtime is False


def test_the_overtime_in_the_state_asked_is_refused():
    with pytest.raises(ConflictError, match="já está ligada"):
        set_overtime(
            CltState(overtime=True), SetOvertime(kind=OVERTIME_ON), DAY, GROWING
        )
    with pytest.raises(ConflictError, match="já está desligada"):
        set_overtime(CltState(), SetOvertime(kind=OVERTIME_OFF), DAY, GROWING)


def test_only_the_clt_has_the_overtime_action():
    with pytest.raises(ConflictError, match="não tem mecânica"):
        apply_action(
            Profession.WELFARE,
            MechanicState(),
            SetOvertime(kind=OVERTIME_ON),
            DAY,
            GROWING,
        )


def test_the_overtime_ends_only_when_it_is_on_and_the_gdp_is_negative():
    assert overtime_ends_with_recession(CltState(overtime=True), RECESSION)
    assert not overtime_ends_with_recession(CltState(overtime=True), ZERO_GROWTH)
    assert not overtime_ends_with_recession(CltState(), RECESSION)


@pytest.mark.parametrize(
    ("overtime", "macro", "reserve", "expected"),
    [
        # Liga com o PIB acima do neutro e o caixa cobrindo o imprevisto de saúde em dobro
        (False, GROWING, COVERED, OVERTIME_ON),
        (False, STAGNANT, COVERED, None),
        (False, GROWING, BROKE, None),
        # Desliga quando uma das duas condições falha, e fica ligada enquanto as duas valem
        (True, STAGNANT, COVERED, OVERTIME_OFF),
        (True, GROWING, BROKE, OVERTIME_OFF),
        (True, GROWING, COVERED, None),
        (True, RECESSION, BROKE, OVERTIME_OFF),
    ],
)
def test_the_policy_turns_the_overtime_on_and_off(overtime, macro, reserve, expected):
    action = overtime_policy(CltState(overtime=overtime), DAY, macro, reserve)

    assert (None if action is None else action.kind) == expected


def test_the_first_month_deposits_eight_percent_of_the_salary(monkeypatch):
    with_tr(monkeypatch, None)
    ana = person("Ana")
    sim = match(monkeypatch)

    assert state_of(sim, ana).fgts_balance == Decimal("640.00")


def test_each_month_the_balance_yields_with_the_tr_and_receives_the_deposit(
    monkeypatch,
):
    with_tr(monkeypatch, "0.5")
    ana = person("Ana")
    sim = match(monkeypatch)
    before = state_of(sim, ana).fgts_balance

    turn_of_month(sim)

    gross = LifeBudget.of(sim.settings).salary_on(DAY)
    expected = before + fgts_yield(before, Decimal("0.005")) + fgts_deposit(gross)
    assert state_of(sim, ana).fgts_balance == expected


def test_without_a_tr_the_balance_yields_only_the_three_percent(monkeypatch):
    with_tr(monkeypatch, None)
    ana = person("Ana")
    sim = match(monkeypatch)
    before = state_of(sim, ana).fgts_balance

    turn_of_month(sim)

    gross = LifeBudget.of(sim.settings).salary_on(DAY)
    expected = before + fgts_yield(before, Decimal(0)) + fgts_deposit(gross)
    assert state_of(sim, ana).fgts_balance == expected


def test_the_deposit_does_not_come_out_of_the_salary(monkeypatch):
    with_tr(monkeypatch, None)
    ana = person("Ana")
    sim = match(monkeypatch)
    cash = sim.get_cash(ana.client_id)

    turn_of_month(sim)

    budget = sim._life_budget(LifeBudget.of(sim.settings), ana.id)
    day = sim.get_current_date()
    assert sim.get_cash(ana.client_id) == (
        cash + budget.net_salary_on(day) - budget.expense_on(day)
    )


def test_the_deposit_counts_the_overtime_in_the_gross(monkeypatch):
    with_tr(monkeypatch, None)
    ana = person("Ana")
    sim = match(monkeypatch)
    with_growth(sim, monkeypatch, GROWING)
    sim.apply_profession_action(ana, SetOvertime(kind=OVERTIME_ON))
    before = state_of(sim, ana).fgts_balance

    turn_of_month(sim)

    life = LifeBudget.of(sim.settings)
    gross = sim._life_budget(life, ana.id).salary_on(sim.get_current_date())
    assert gross == LifeBudget.of(sim.settings).salary_on(DAY) * Decimal("1.25")
    assert state_of(sim, ana).fgts_balance == (
        before + fgts_yield(before, Decimal(0)) + fgts_deposit(gross)
    )


def test_a_month_without_salary_does_not_deposit(monkeypatch):
    with_tr(monkeypatch, None)
    ana = person("Ana")
    sim = match(monkeypatch)
    before = state_of(sim, ana).fgts_balance
    # O salário do mês seguinte não entra: a demissão sorteada o tirou
    monkeypatch.setattr(
        simulation_module, "salary_skipped", lambda *args, **kwargs: True
    )

    turn_of_month(sim)

    assert state_of(sim, ana).fgts_balance == before + fgts_yield(before, Decimal(0))


def test_the_layoff_pays_the_balance_plus_the_fine_into_the_cash(monkeypatch):
    with_tr(monkeypatch, None)
    ana = person("Ana")
    sim = match(monkeypatch)
    layoff = with_layoff_on_demand(monkeypatch)
    mid_month(sim)
    balance = state_of(sim, ana).fgts_balance
    cash = sim.get_cash(ana.client_id)

    layoff["on"] = True
    sim.next_tick()

    assert sim.get_cash(ana.client_id) == cash + fgts_payout(balance)
    assert state_of(sim, ana) == CltState()
    assert balance > 0


def test_the_layoff_of_ten_thousand_puts_fourteen_thousand_in_the_cash(monkeypatch):
    with_tr(monkeypatch, None)
    ana = person("Ana")
    sim = match(monkeypatch)
    layoff = with_layoff_on_demand(monkeypatch)
    mid_month(sim)
    sim._profession_book.save_state(ana.id, CltState(fgts_balance=Decimal(10000)))
    cash = sim.get_cash(ana.client_id)

    layoff["on"] = True
    sim.next_tick()

    assert sim.get_cash(ana.client_id) == cash + Decimal(14000)


def test_the_layoff_leaves_a_withdrawal_row_in_the_history(monkeypatch):
    with_tr(monkeypatch, None)
    ana = person("Ana")
    sim = match(monkeypatch)
    layoff = with_layoff_on_demand(monkeypatch)
    mid_month(sim)
    sim._profession_book.save_state(ana.id, CltState(fgts_balance=Decimal(10000)))

    layoff["on"] = True
    sim.next_tick()

    rows = life_history(sim, ana.client_id)
    [withdrawal] = [r for r in rows if r.kind is LifeHistoryKind.FGTS_WITHDRAWAL]
    assert withdrawal.category is LifeHistoryCategory.PROFESSION
    assert withdrawal.amount == Decimal(14000)
    assert withdrawal.event_date == sim.get_current_date()
    kinds = [r.kind for r in rows]
    assert kinds.index(LifeHistoryKind.LAYOFF) < kinds.index(
        LifeHistoryKind.FGTS_WITHDRAWAL
    )


def test_the_withdrawal_is_a_cash_inflow_that_is_not_a_contribution():
    event = CashflowEventType.FGTS_WITHDRAWAL

    assert event.sign == 1
    assert not event.is_contribution


def test_the_layoff_turns_the_overtime_off(monkeypatch):
    with_tr(monkeypatch, None)
    ana = person("Ana")
    sim = match(monkeypatch)
    with_growth(sim, monkeypatch, GROWING)
    layoff = with_layoff_on_demand(monkeypatch)
    sim.apply_profession_action(ana, SetOvertime(kind=OVERTIME_ON))
    mid_month(sim)
    assert state_of(sim, ana).overtime

    layoff["on"] = True
    sim.next_tick()

    assert not state_of(sim, ana).overtime


def test_the_layoff_of_an_empty_account_pays_nothing_and_adds_no_row(monkeypatch):
    with_tr(monkeypatch, None)
    ana = person("Ana")
    sim = match(monkeypatch)
    layoff = with_layoff_on_demand(monkeypatch)
    mid_month(sim)
    sim._profession_book.save_state(ana.id, CltState())
    cash = sim.get_cash(ana.client_id)

    layoff["on"] = True
    sim.next_tick()

    assert sim.get_cash(ana.client_id) == cash
    assert not [
        r
        for r in life_history(sim, ana.client_id)
        if r.kind is LifeHistoryKind.FGTS_WITHDRAWAL
    ]


def test_the_locked_balance_is_in_the_networth_by_the_single_definition(monkeypatch):
    with_tr(monkeypatch, None)
    ana = person("Ana")
    sim = match(monkeypatch)
    sim._profession_book.save_state(ana.id, CltState(fgts_balance=Decimal(10000)))

    portfolio = sim.get_portfolio(ana.client_id)
    snapshot = sim._balance_snapshot(ana)
    sheet = sim._engine.balance_sheet(ana.client_id)

    assert portfolio.locked_value == Decimal(10000)
    assert sheet.total_locked == Decimal(10000)
    expected = networth(
        cash=portfolio.cash,
        equity=portfolio.variable_income_value,
        fixed=portfolio.fixed_income_value,
        locked=Decimal(10000),
        debt=portfolio.debt,
    )
    assert portfolio.total_networth == expected
    assert snapshot.total_networth == expected
    assert sim._engine.networth(ana.client_id, portfolio.debt) == expected
    assert portfolio.assets_value == expected + portfolio.debt
    assert portfolio.locked_networth_pct == Decimal(10000) / portfolio.assets_value


def test_the_portfolio_shares_with_the_locked_class_still_add_up_to_one(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim._profession_book.save_state(ana.id, CltState(fgts_balance=Decimal(10000)))

    portfolio = sim.get_portfolio(ana.client_id)

    assert (
        portfolio.variable_income_networth_pct
        + portfolio.fixed_income_networth_pct
        + portfolio.cash_pct
        + portfolio.locked_networth_pct
    ) == pytest.approx(Decimal(1))


def test_the_snapshot_records_the_locked_balance_and_the_networth_sums_it(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim._profession_book.save_state(ana.id, CltState(fgts_balance=Decimal(10000)))
    portfolio_id = SimulationManager.get_portfolio_id(ana.id)

    [entry] = sim._snapshot_users([ana])
    stored = repository.portfolio.get_patrimonial_history(portfolio_id)[-1]

    assert entry.snapshot.total_locked == Decimal(10000)
    assert stored.total_locked == Decimal(10000)
    assert stored.total_networth == (
        stored.total_cash
        + stored.total_equity
        + stored.total_fixed
        + stored.total_locked
        - stored.total_debt
    )
    assert stored.total_networth == networth(
        cash=stored.total_cash,
        equity=stored.total_equity,
        fixed=stored.total_fixed,
        locked=Decimal(10000),
        debt=stored.total_debt,
    )


def test_the_ranking_networth_that_is_stored_counts_the_locked_balance(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim._profession_book.save_state(ana.id, CltState(fgts_balance=Decimal(10000)))
    cash_only = networth(
        cash=sim.get_cash(ana.client_id),
        equity=Decimal(0),
        fixed=Decimal(0),
        locked=Decimal(0),
        debt=Decimal(0),
    )

    stored = sim._balance_snapshot(ana).total_networth

    assert stored == cash_only + Decimal(10000)


def test_the_locked_balance_is_zero_outside_the_clt_and_outside_the_professions_mode(
    monkeypatch,
):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim.switch_profession(ana, Profession.WELFARE)

    assert sim.get_portfolio(ana.client_id).locked_value == 0
    assert type(sim.get_profession_state(ana.client_id).state) is MechanicState
    assert sim._clt_state_of(ana.id) is None


def test_a_match_without_professions_has_no_fgts_and_no_overtime(monkeypatch):
    ana = person("Ana")
    settings = rules(unexpected_per_year=0)
    monkeypatch.setattr(SettingsManager, "_settings", settings)
    SimulationLoader.create(settings)
    sim = SimulationManager.get_active_simulation()
    turn_of_month(sim)

    assert sim._clt_state_of(ana.id) is None
    assert sim.get_portfolio(ana.client_id).locked_value == 0
    assert "profissões" in refusal(
        lambda: sim.apply_profession_action(ana, SetOvertime(kind=OVERTIME_ON))
    )


def test_the_overtime_action_is_logged_and_the_state_is_saved_and_read_back(
    monkeypatch,
):
    ana = person("Ana")
    sim = match(monkeypatch)
    with_growth(sim, monkeypatch, GROWING)

    sim.apply_profession_action(ana, SetOvertime(kind=OVERTIME_ON))
    sim.apply_profession_action(ana, SetOvertime(kind=OVERTIME_OFF))
    sim.apply_profession_action(ana, SetOvertime(kind=OVERTIME_ON))

    stored = repository.profession.states(sim.settings.id)[ana.id]
    assert isinstance(stored, CltState) and stored.overtime
    assert stored.fgts_balance == state_of(sim, ana).fgts_balance
    keys = [
        r.life_event_key
        for r in life_history(sim, ana.client_id)
        if r.kind is LifeHistoryKind.PROFESSION_ACTION
    ]
    assert keys == [OVERTIME_ON, OVERTIME_OFF, OVERTIME_ON]


def test_the_overtime_cannot_be_turned_on_in_a_recession(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    with_growth(sim, monkeypatch, RECESSION)

    assert "PIB" in refusal(
        lambda: sim.apply_profession_action(ana, SetOvertime(kind=OVERTIME_ON))
    )
    assert not state_of(sim, ana).overtime


def test_the_overtime_turns_off_by_itself_when_the_month_turns_in_a_recession(
    monkeypatch,
):
    ana = person("Ana")
    sim = match(monkeypatch)
    with_growth(sim, monkeypatch, GROWING)
    sim.apply_profession_action(ana, SetOvertime(kind=OVERTIME_ON))
    with_growth(sim, monkeypatch, RECESSION)

    turn_of_month(sim)

    assert not state_of(sim, ana).overtime
    keys = [
        r.life_event_key
        for r in life_history(sim, ana.client_id)
        if r.kind is LifeHistoryKind.PROFESSION_ACTION
    ]
    assert keys == [OVERTIME_ON, OVERTIME_ENDED]


def test_the_overtime_ends_before_the_income_of_the_month_is_paid(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    with_growth(sim, monkeypatch, GROWING)
    sim.apply_profession_action(ana, SetOvertime(kind=OVERTIME_ON))
    with_growth(sim, monkeypatch, RECESSION)
    cash = sim.get_cash(ana.client_id)

    turn_of_month(sim)

    budget = sim._life_budget(LifeBudget.of(sim.settings), ana.id)
    day = sim.get_current_date()
    assert sim.get_cash(ana.client_id) == (
        cash + budget.net_salary_on(day) - budget.expense_on(day)
    )


def test_the_health_event_costs_double_with_the_overtime_on(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch, starting_cash=RICH)
    with_growth(sim, monkeypatch, GROWING)
    health = next(e for e in DEFAULT_LIFE_EVENTS if e.key == "HEALTH")
    switch = {"on": False}
    monkeypatch.setattr(
        simulation_module,
        "unexpected_on",
        lambda seed, day, *args, **kwargs: health if switch["on"] else None,
    )
    mid_month(sim)

    def cost() -> Decimal:
        before = sim.get_cash(ana.client_id)
        switch["on"] = True
        sim.next_tick()
        switch["on"] = False
        return before - sim.get_cash(ana.client_id)

    normal = cost()
    sim.apply_profession_action(ana, SetOvertime(kind=OVERTIME_ON))
    doubled = cost()

    assert normal > 0
    assert doubled == 2 * normal


@pytest.fixture
def idle_strategy(monkeypatch: pytest.MonkeyPatch) -> None:
    """A estratégia de CDI deixa o caixa parado: a reserva do bot é o caixa de partida."""
    monkeypatch.setattr(CdiReference, "next", lambda self, ctx, params: None)


def test_the_bot_turns_the_overtime_on_by_the_policy_and_the_human_does_not(
    idle_strategy, monkeypatch
):
    ana = person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.CLT)
    )
    sim = match(monkeypatch, starting_cash=RICH)
    with_growth(sim, monkeypatch, GROWING)
    turn_of_month(sim)

    assert state_of(sim, bot).overtime
    assert not state_of(sim, ana).overtime


def test_the_bot_counts_the_fixed_income_the_auto_cover_reaches_as_reserve(
    idle_strategy, monkeypatch
):
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.CLT)
    )
    sim = match(monkeypatch, starting_cash=RICH)
    # O caixa inteiro vai para um CDB de liquidez diária: o bot fica sem caixa
    cdb = next(
        asset
        for asset in sim._engine.fixed_income_market.get_available_assets()
        if asset.daily_liquidity and asset.investment_type is FixedIncomeType.CDB
    )
    sim._engine.fixed_broker.buy(
        bot.client_id, cdb, sim._engine.get_cash(bot.client_id)
    )
    assert sim._engine.get_cash(bot.client_id) == 0
    assert sim._engine.coverable_cash(bot.client_id) >= COVERED.cash
    with_growth(sim, monkeypatch, GROWING)

    turn_of_month(sim)

    assert state_of(sim, bot).overtime


def test_the_bot_turns_the_overtime_off_when_the_economy_stops_growing(
    idle_strategy, monkeypatch
):
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.CLT)
    )
    sim = match(monkeypatch, starting_cash=RICH)
    with_growth(sim, monkeypatch, GROWING)
    turn_of_month(sim)
    assert state_of(sim, bot).overtime

    with_growth(sim, monkeypatch, STAGNANT)
    turn_of_month(sim)

    assert not state_of(sim, bot).overtime


def test_the_route_turns_the_overtime_on_and_off(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    with_growth(sim, monkeypatch, GROWING)
    app = FastAPI()
    app.include_router(simulation_router)
    app.dependency_overrides[get_client_id] = lambda: ana.client_id
    client = TestClient(app)

    on = client.post("/api/simulation/overtime", json={"enabled": True})
    again = client.post("/api/simulation/overtime", json={"enabled": True})
    off = client.post("/api/simulation/overtime", json={"enabled": False})

    assert on.status_code == 200
    assert on.json()["state"]["overtime"] is True
    assert again.status_code == 409
    assert off.json()["state"]["overtime"] is False


def test_the_route_refuses_the_overtime_in_a_recession(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    with_growth(sim, monkeypatch, RECESSION)
    app = FastAPI()
    app.include_router(simulation_router)
    app.dependency_overrides[get_client_id] = lambda: ana.client_id

    response = TestClient(app).post("/api/simulation/overtime", json={"enabled": True})

    assert response.status_code == 409
    assert not state_of(sim, ana).overtime


def test_the_state_resumes_with_the_balance_and_the_overtime(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    with_growth(sim, monkeypatch, GROWING)
    sim.apply_profession_action(ana, SetOvertime(kind=OVERTIME_ON))
    turn_of_month(sim)

    reread = ProfessionBook(sim.settings.id).state_of(ana.id, Profession.CLT)

    assert reread == state_of(sim, ana)
    assert isinstance(reread, CltState) and reread.fgts_balance > 0
