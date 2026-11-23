"""O consignado do Servidor na partida: elegibilidade, parcela na virada do mês, rotas e a política do bot."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.enum import (
    CashflowEventType,
    CreditEventType,
    FixedIncomeType,
    Profession,
)
from backend.core.life_budget import LifeBudget
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.credit.rules import PAYROLL_MARGIN, payroll_first_collection
from backend.features.simulation import simulation as simulation_module
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.strategy.bots import resolve_bot
from backend.features.strategy.cdi import CdiReference
from backend.routes.credit import credit_router
from backend.routes.dependencies import get_client_id
from tests.test_bots import (  # noqa: F401
    person,
    refusal,
    room,
    rules,
    started,
)
from tests.test_clt import turn_of_month
from tests.test_profession_mechanics import match

# Caixa de partida folgado para o bot
RICH = Decimal(100000)

pytestmark = pytest.mark.usefixtures("room")


def servant_match(monkeypatch: pytest.MonkeyPatch, **changes: object):
    """Uma partida com um jogador Servidor, sem imprevistos, e o jogador."""
    ana = person("Ana")
    sim = match(monkeypatch, **changes)
    sim.switch_profession(ana, Profession.PUBLIC_SERVANT)
    return sim, ana


def net_salary(sim: Simulation, user) -> Decimal:
    budget = sim._life_budget(LifeBudget.of(sim.settings), user.id)
    return budget.net_salary_on(sim.get_current_date())


def max_amount(sim: Simulation, user, term: int = 24) -> Decimal:
    return sim.quote_payroll(user, user.client_id, Decimal(1000), term).max_amount


def turn_of_first_installment(sim: Simulation, client_id: UUID) -> tuple[date, Decimal]:
    """
    Avança até a virada em que cai a primeira parcela do consignado e devolve o dia
    e o caixa de um instante antes dela.
    """
    first = payroll_first_collection(sim.get_current_date())
    while True:
        cash_before = sim.get_cash(client_id)
        day = turn_of_month(sim)
        if day >= first:
            assert day == first
            return day, cash_before


def cashflow(sim: Simulation, client_id: UUID):
    EventManager.flush()
    return repository.event.get_cashflow_events(
        sim.settings.id, UserManager.get_portfolio_id(client_id)
    )


def credit_types(sim: Simulation, user) -> list[CreditEventType]:
    EventManager.flush()
    return [
        e.event_type for e in repository.credit.get_events(sim.settings.id, user.id)
    ]


# =========================
# Quem pode tomar
# =========================


def test_only_the_public_servant_can_take_the_consignado(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)

    message = refusal(
        lambda: sim.contract_payroll(ana, ana.client_id, Decimal(1000), 12)
    )

    assert "Servidor" in message
    assert sim.get_credit(ana, ana.client_id).debt == 0
    assert credit_types(sim, ana) == []


def test_the_quote_is_refused_outside_the_public_servant(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)

    refusal(lambda: sim.quote_payroll(ana, ana.client_id, Decimal(1000), 12))


def test_a_match_without_professions_refuses_the_consignado(monkeypatch):
    ana = person("Ana")
    settings = rules(unexpected_per_year=0)
    monkeypatch.setattr(SettingsManager, "_settings", settings)
    SimulationLoader.create(settings)
    sim = SimulationManager.get_active_simulation()

    message = refusal(
        lambda: sim.contract_payroll(ana, ana.client_id, Decimal(1000), 12)
    )

    assert "Servidor" in message


def test_the_fund_account_cannot_take_the_consignado(monkeypatch):
    sim, ana = servant_match(monkeypatch)

    message = refusal(lambda: sim.contract_payroll(ana, uuid4(), Decimal(1000), 12))

    assert "conta pessoal" in message


# =========================
# Contratar e a virada do mês
# =========================


def test_the_servant_contracts_and_the_money_falls_in_the_cash(monkeypatch):
    sim, ana = servant_match(monkeypatch)
    cash = sim.get_cash(ana.client_id)

    loan = sim.contract_payroll(ana, ana.client_id, Decimal(5000), 24)

    assert sim.get_cash(ana.client_id) == cash + 5000
    assert loan.principal == Decimal(5000)
    assert loan.total_installments == 24
    assert credit_types(sim, ana) == [CreditEventType.PAYROLL_CONTRACT]
    overview = sim.get_credit(ana, ana.client_id)
    assert overview.loans == [] and overview.open_loans == 1
    assert len(overview.payroll_loans) == 1
    assert overview.debt == Decimal(5000)


def test_a_consignado_over_the_margin_is_refused_and_leaves_the_cash(monkeypatch):
    sim, ana = servant_match(monkeypatch)
    cash = sim.get_cash(ana.client_id)
    over = max_amount(sim, ana) * 2

    message = refusal(lambda: sim.contract_payroll(ana, ana.client_id, over, 24))

    assert "margem" in message
    assert sim.get_cash(ana.client_id) == cash


def test_the_margin_is_the_share_of_the_net_salary_of_the_month(monkeypatch):
    sim, ana = servant_match(monkeypatch)

    quote = sim.quote_payroll(ana, ana.client_id, Decimal(1000), 24)

    assert quote.net_salary == net_salary(sim, ana)
    assert quote.margin == quote.net_salary * PAYROLL_MARGIN


def test_the_installment_leaves_at_the_month_turn_as_its_own_entry(monkeypatch):
    sim, ana = servant_match(monkeypatch)
    loan = sim.contract_payroll(ana, ana.client_id, Decimal(5000), 24)
    budget = sim._life_budget(LifeBudget.of(sim.settings), ana.id)

    day, cash = turn_of_first_installment(sim, ana.client_id)

    rows = [r for r in cashflow(sim, ana.client_id) if r.event_date == day]
    [salary] = [r for r in rows if r.event_type is CashflowEventType.SALARY]
    [payment] = [r for r in rows if r.event_type is CashflowEventType.PAYROLL_PAYMENT]
    assert payment.amount == loan.installment
    assert salary.amount == budget.net_salary_on(day)
    assert sim.get_cash(ana.client_id) == (
        cash + salary.amount - payment.amount - budget.expense_on(day)
    )
    types = credit_types(sim, ana)
    assert types.count(CreditEventType.PAYROLL_INSTALLMENT) == 1
    assert CreditEventType.INSTALLMENT_LATE not in types


def test_the_contract_late_in_the_month_skips_the_next_turn(monkeypatch):
    # A partida abre em 29/3: a virada de abril fica a 3 dias e a de maio, a 35
    sim, ana = servant_match(monkeypatch)
    loan = sim.contract_payroll(ana, ana.client_id, Decimal(5000), 24)

    assert turn_of_month(sim).month == 4
    assert credit_types(sim, ana).count(CreditEventType.PAYROLL_INSTALLMENT) == 0
    assert turn_of_month(sim).month == 5
    types = credit_types(sim, ana)
    assert types.count(CreditEventType.PAYROLL_INSTALLMENT) == 1
    [payment] = [
        r
        for r in cashflow(sim, ana.client_id)
        if r.event_type is CashflowEventType.PAYROLL_PAYMENT
    ]
    assert payment.amount == loan.installment


def test_the_contract_on_the_first_trading_day_pays_in_the_next_month(monkeypatch):
    sim, ana = servant_match(monkeypatch, start_date=date(2004, 3, 1))
    sim.contract_payroll(ana, ana.client_id, Decimal(5000), 24)

    turn_of_month(sim)

    assert credit_types(sim, ana).count(CreditEventType.PAYROLL_INSTALLMENT) == 1


def with_small_salary(monkeypatch: pytest.MonkeyPatch, value: Decimal) -> None:
    """O salário líquido do mês que a partida paga, menor que a parcela."""
    monkeypatch.setattr(
        LifeBudget, "net_salary_on", lambda self, day, income_lost=False: value
    )


def test_a_salary_below_the_installment_leaves_the_rest_to_the_cash(monkeypatch):
    sim, ana = servant_match(monkeypatch)
    loan = sim.contract_payroll(ana, ana.client_id, Decimal(5000), 24)
    budget = sim._life_budget(LifeBudget.of(sim.settings), ana.id)
    small = loan.installment / 2
    with_small_salary(monkeypatch, small)

    day, cash = turn_of_first_installment(sim, ana.client_id)

    rows = [r for r in cashflow(sim, ana.client_id) if r.event_date == day]
    [salary] = [r for r in rows if r.event_type is CashflowEventType.SALARY]
    [payment] = [r for r in rows if r.event_type is CashflowEventType.PAYROLL_PAYMENT]
    assert salary.amount == small
    assert payment.amount == loan.installment
    assert sim.get_cash(ana.client_id) == (
        cash + small - loan.installment - budget.expense_on(day)
    )
    assert CreditEventType.INSTALLMENT_LATE not in credit_types(sim, ana)


def test_the_installment_sells_fixed_income_when_the_cash_falls_short(monkeypatch):
    sim, ana = servant_match(monkeypatch, starting_cash=RICH)
    sim.contract_payroll(ana, ana.client_id, Decimal(5000), 24)
    cdb = next(
        asset
        for asset in sim._engine.fixed_income_market.get_available_assets()
        if asset.daily_liquidity and asset.investment_type is FixedIncomeType.CDB
    )
    sim._engine.fixed_broker.buy(
        ana.client_id, cdb, sim._engine.get_cash(ana.client_id)
    )
    assert sim._engine.get_cash(ana.client_id) == 0
    with_small_salary(monkeypatch, Decimal(0))
    fixed_before = sim._engine.coverable_cash(ana.client_id)

    turn_of_first_installment(sim, ana.client_id)

    assert sim._engine.coverable_cash(ana.client_id) < fixed_before
    assert sim.get_cash(ana.client_id) >= 0
    assert CreditEventType.PAYROLL_INSTALLMENT in credit_types(sim, ana)


def test_the_consignado_debt_enters_the_snapshot_and_the_networth(monkeypatch):
    sim, ana = servant_match(monkeypatch)
    before = sim._engine.networth(ana.client_id, Decimal(0))

    sim.contract_payroll(ana, ana.client_id, Decimal(5000), 24)

    debt = sim._engine.credit_book.debt(ana.client_id, sim.get_current_date())
    assert debt == Decimal(5000)
    # O dinheiro entra no caixa e a dívida sai: o patrimônio fica onde estava
    assert sim._engine.networth(ana.client_id, debt) == before


def test_the_consignado_reduces_the_common_loan_limit(monkeypatch):
    sim, ana = servant_match(monkeypatch)
    before = sim.get_credit(ana, ana.client_id).offer

    sim.contract_payroll(ana, ana.client_id, Decimal(5000), 24)

    after = sim.get_credit(ana, ana.client_id).offer
    assert after.annual_rate == before.annual_rate
    assert before.max_amount - after.max_amount == Decimal(5000)


def test_the_payoff_route_service_closes_the_consignado(monkeypatch):
    sim, ana = servant_match(monkeypatch)
    loan = sim.contract_payroll(ana, ana.client_id, Decimal(5000), 24)

    sim.payoff_loan(ana, ana.client_id, loan.id)

    assert sim._engine.credit_book.payroll_loans(ana.client_id) == []
    assert credit_types(sim, ana)[-1] is CreditEventType.PAYOFF


def test_the_state_resumes_with_the_consignado(monkeypatch):
    sim, ana = servant_match(monkeypatch)
    loan = sim.contract_payroll(ana, ana.client_id, Decimal(5000), 24)
    turn_of_first_installment(sim, ana.client_id)
    EventManager.flush()
    book = sim._engine.credit_book
    [live] = book.payroll_loans(ana.client_id)

    # Sem o estado em memória, o livro lê os eventos gravados
    book.forget(ana.client_id)

    [back] = book.payroll_loans(ana.client_id)
    assert back.loan_id == loan.id == live.loan_id
    assert back.state == live.state
    assert back.paid_installments == 1


# =========================
# Rotas
# =========================


def credit_client(user) -> TestClient:
    app = FastAPI()
    app.include_router(credit_router)
    app.dependency_overrides[get_client_id] = lambda: user.client_id
    return TestClient(app)


def test_the_quote_route_reads_the_installment_and_the_margin(monkeypatch):
    sim, ana = servant_match(monkeypatch)

    response = credit_client(ana).get(
        "/api/credit/payroll/quote", params={"amount": 3000, "term_months": 24}
    )

    assert response.status_code == 200, response.text
    body = response.json()
    expected = sim.quote_payroll(ana, ana.client_id, Decimal(3000), 24)
    assert Decimal(body["installment"]) == expected.installment
    assert Decimal(body["margin_free"]) == expected.margin_free
    assert Decimal(body["max_amount"]) == expected.max_amount
    assert body["fits_margin"] is True


def test_the_contract_route_creates_the_consignado_and_returns_its_id(monkeypatch):
    sim, ana = servant_match(monkeypatch)
    http = credit_client(ana)

    response = http.post(
        "/api/credit/payroll", json={"amount": "3000", "term_months": 24}
    )

    assert response.status_code == 200, response.text
    [loan] = sim._engine.credit_book.payroll_loans(ana.client_id)
    assert response.json()["id"] == str(loan.loan_id)
    assert http.get("/api/credit").json()["loans"] == []

    paid_off = http.post(f"/api/credit/loans/{loan.loan_id}/payoff")
    assert paid_off.status_code == 204, paid_off.text
    assert sim._engine.credit_book.payroll_loans(ana.client_id) == []


def test_the_routes_refuse_outside_the_servant_and_over_the_margin(monkeypatch):
    sim, ana = servant_match(monkeypatch)
    http = credit_client(ana)
    over = max_amount(sim, ana) * 2

    too_much = http.post(
        "/api/credit/payroll", json={"amount": str(over), "term_months": 24}
    )
    bad_term = http.get(
        "/api/credit/payroll/quote", params={"amount": 3000, "term_months": 5}
    )
    sim.switch_profession(ana, Profession.CLT)
    clt = http.get(
        "/api/credit/payroll/quote", params={"amount": 3000, "term_months": 24}
    )

    assert too_much.status_code == 409
    assert bad_term.status_code == 422
    assert clt.status_code == 409


# =========================
# A política do Servidor-bot
# =========================


@pytest.fixture
def idle_strategy(monkeypatch: pytest.MonkeyPatch) -> None:
    """A estratégia de CDI deixa o caixa parado: o dinheiro do consignado fica no caixa."""
    monkeypatch.setattr(CdiReference, "next", lambda self, ctx, params: None)


def with_drawdown(monkeypatch: pytest.MonkeyPatch, value: str | None) -> None:
    """O quanto o Ibovespa está abaixo do topo de 12 meses que a partida vê."""
    monkeypatch.setattr(
        simulation_module,
        "stocks_drawdown",
        lambda day, **_: Decimal(value) if value is not None else None,
    )


def servant_bot_match(monkeypatch: pytest.MonkeyPatch):
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.PUBLIC_SERVANT)
    )
    return match(monkeypatch, starting_cash=RICH), bot


def payroll_of(sim: Simulation, user):
    return sim._engine.credit_book.payroll_loans(user.client_id)


def test_the_bot_takes_the_consignado_at_minus_twenty_in_24_months(
    idle_strategy, monkeypatch
):
    sim, bot = servant_bot_match(monkeypatch)
    with_drawdown(monkeypatch, "0.20")
    cash = sim.get_cash(bot.client_id)

    turn_of_month(sim)

    [loan] = payroll_of(sim, bot)
    assert loan.total_installments == 24
    expected_margin = (net_salary(sim, bot) * PAYROLL_MARGIN) / 2
    assert loan.state.installment <= expected_margin
    assert sim.get_cash(bot.client_id) > cash


def test_the_bot_does_not_take_at_minus_nineteen(idle_strategy, monkeypatch):
    sim, bot = servant_bot_match(monkeypatch)
    with_drawdown(monkeypatch, "0.19")

    turn_of_month(sim)

    assert payroll_of(sim, bot) == []


def test_the_bot_does_not_take_again_with_an_active_consignado(
    idle_strategy, monkeypatch
):
    sim, bot = servant_bot_match(monkeypatch)
    with_drawdown(monkeypatch, "0.30")
    turn_of_month(sim)
    [first] = payroll_of(sim, bot)

    turn_of_month(sim)

    [only] = payroll_of(sim, bot)
    assert only.loan_id == first.loan_id


def test_the_bot_decides_only_at_the_month_turn(idle_strategy, monkeypatch):
    sim, bot = servant_bot_match(monkeypatch)
    with_drawdown(monkeypatch, "0.30")

    sim.next_tick()
    assert sim.get_current_date().month == 3
    assert payroll_of(sim, bot) == []

    turn_of_month(sim)
    assert len(payroll_of(sim, bot)) == 1


def test_the_human_servant_never_gets_the_consignado_by_policy(
    idle_strategy, monkeypatch
):
    sim, ana = servant_match(monkeypatch)
    with_drawdown(monkeypatch, "0.30")

    turn_of_month(sim)

    assert payroll_of(sim, ana) == []


def test_the_bot_pays_off_when_the_index_returns_under_five_percent(
    idle_strategy, monkeypatch
):
    sim, bot = servant_bot_match(monkeypatch)
    with_drawdown(monkeypatch, "0.30")
    turn_of_month(sim)
    assert len(payroll_of(sim, bot)) == 1

    with_drawdown(monkeypatch, "0.10")
    turn_of_month(sim)
    assert len(payroll_of(sim, bot)) == 1

    with_drawdown(monkeypatch, "0.04")
    turn_of_month(sim)

    assert payroll_of(sim, bot) == []
    assert credit_types(sim, bot)[-1] is CreditEventType.PAYOFF


def test_the_bot_sells_fixed_income_to_pay_off_when_the_cash_falls_short(
    idle_strategy, monkeypatch
):
    sim, bot = servant_bot_match(monkeypatch)
    with_drawdown(monkeypatch, "0.30")
    turn_of_month(sim)
    # Todo o caixa vai para um CDB de liquidez diária: a quitação precisa vendê-lo
    cdb = next(
        asset
        for asset in sim._engine.fixed_income_market.get_available_assets()
        if asset.daily_liquidity and asset.investment_type is FixedIncomeType.CDB
    )
    sim._engine.fixed_broker.buy(
        bot.client_id, cdb, sim._engine.get_cash(bot.client_id)
    )
    assert sim._engine.get_cash(bot.client_id) == 0
    fixed_before = sim._engine.coverable_cash(bot.client_id)

    with_drawdown(monkeypatch, "0.02")
    turn_of_month(sim)

    assert payroll_of(sim, bot) == []
    assert sim._engine.coverable_cash(bot.client_id) < fixed_before


def test_the_bot_without_the_index_series_does_nothing(idle_strategy, monkeypatch):
    sim, bot = servant_bot_match(monkeypatch)
    with_drawdown(monkeypatch, None)

    turn_of_month(sim)

    assert payroll_of(sim, bot) == []


def test_a_bot_of_another_profession_never_takes_it(idle_strategy, monkeypatch):
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.CLT)
    )
    sim = match(monkeypatch, starting_cash=RICH)
    with_drawdown(monkeypatch, "0.30")

    turn_of_month(sim)

    assert payroll_of(sim, bot) == []
    assert date(2004, 4, 1) <= sim.get_current_date()
