"""Crédito da conta da gestora pela fachada da partida, com banco: só o principal contrata, a taxa a pagar sai do dinheiro novo e o atraso aponta para a gestora."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from backend.core import repository
from backend.core.dto.fund import FundContributionRequest, FundMergeProposalRequest
from backend.core.enum import PendingType
from backend.core.exceptions.http_exceptions import ConflictError, ForbiddenError
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.features.credit.credit_book import replay
from tests.test_fund_comanagers import active_comanager
from tests.test_fund_flow import book_of, found_request, fund_with_cash, player
from tests.test_fund_simulation import TICKER, empty_match
from tests.test_simulation_loader import started  # noqa: F401


@pytest.fixture
def match(started):  # noqa: F811
    """A gestora da Ana listada, com 5.000 em caixa; Bruno é jogador."""
    sim, ana = empty_match("Bruno")
    fund_id = fund_with_cash(sim, ana)
    sim.open_fund_offer(ana, fund_id, 20)
    sim.close_fund_offer(ana, fund_id)
    fund = book_of(sim).get(TICKER)
    return sim, ana, player(sim, "Bruno"), fund.account.client_id


def test_the_principal_borrows_on_the_fund_account(match):
    sim, ana, _bruno, fund_client = match
    cash = sim._engine.get_cash(fund_client)
    personal = sim._engine.get_cash(ana.client_id)

    sim.contract_loan(ana, fund_client, Decimal(2000), 12)

    assert sim._engine.get_cash(fund_client) == cash + 2000
    assert sim._engine.get_cash(ana.client_id) == personal
    overview = sim.get_credit(ana, fund_client)
    assert overview.loan_debt == 2000
    assert overview.fee_payable == 0
    assert [loan.number for loan in overview.loans] == [1]
    assert sim.get_credit(ana, ana.client_id).loans == []
    assert len(sim._engine.credit_book.loans(fund_client)) == 1


def test_the_quote_of_the_fund_carries_the_fund_fields(match):
    sim, ana, _bruno, fund_client = match

    quote = sim.quote_loan(ana, fund_client, Decimal(2000), 12)

    quotas = book_of(sim).get(TICKER).account.quotas
    assert quote.first_month_interest_per_quota == quote.schedule[0].interest / quotas
    assert quote.fee_payable_settled == 0
    assert quote.debt_after == 2000
    assert sim.quote_loan(ana, ana.client_id, Decimal(2000), 12).debt_after is None


def test_the_new_money_settles_the_payable_fee_at_once(match):
    sim, ana, _bruno, fund_client = match
    fund = book_of(sim).get(TICKER)
    fund.terms = fund.terms.model_copy(update={"management_fee_payable": Decimal(300)})
    sim._engine.fund_fee_payable[fund_client] = Decimal(300)
    cash = sim._engine.get_cash(fund_client)
    personal = sim._engine.get_cash(ana.client_id)

    sim.contract_loan(ana, fund_client, Decimal(2000), 12)

    assert fund.terms.fee_payable == 0
    assert sim._engine.fund_fee_payable[fund_client] == 0
    assert sim._engine.get_cash(fund_client) == cash + 2000 - 300
    assert sim._engine.get_cash(ana.client_id) == personal + 300


def test_the_comanager_does_not_borrow_for_the_fund(match):
    sim, ana, bruno, fund_client = match
    active_comanager(sim, ana, book_of(sim).get(TICKER).terms.id, bruno)

    for call in (
        lambda: sim.get_credit(bruno, fund_client),
        lambda: sim.quote_loan(bruno, fund_client, Decimal(100), 12),
        lambda: sim.contract_loan(bruno, fund_client, Decimal(100), 12),
    ):
        with pytest.raises(ForbiddenError) as raised:
            call()
        assert raised.value.code == "credit_comanager"


def test_the_sovereign_fund_does_not_borrow(match):
    sim, ana, _bruno, _fund_client = match
    sovereign = SimpleNamespace(client_id=ana.client_id.__class__(int=1))
    sim._government = SimpleNamespace(sovereign_fund=lambda: sovereign)

    with pytest.raises(ForbiddenError) as raised:
        sim.contract_loan(ana, sovereign.client_id, Decimal(100), 12)

    assert raised.value.code == "credit_sovereign_fund"


def test_an_unlisted_fund_does_not_borrow(started):  # noqa: F811
    sim, ana = empty_match()
    fund_id = fund_with_cash(sim, ana)
    fund_client = book_of(sim).get(TICKER).account.client_id
    assert fund_id

    with pytest.raises(ConflictError, match="depois da oferta pública"):
        sim.contract_loan(ana, fund_client, Decimal(100), 12)


def test_the_overdue_installment_is_a_pending_that_names_the_fund(match):
    sim, ana, _bruno, fund_client = match
    sim.contract_loan(ana, fund_client, Decimal(2000), 12)
    # Sem caixa na gestora a parcela não é paga e vira atraso
    sim._engine.add_cash(fund_client, -sim._engine.get_cash(fund_client))
    due = sim._engine.credit_book.loans(fund_client)[0].state.next_due

    while sim._engine.current_date <= due + timedelta(days=1):
        sim.next_tick()

    overdue = [
        p
        for p in sim.get_pending(ana)
        if p.type is PendingType.OVERDUE_INSTALLMENT and p.fund_id is not None
    ]
    assert len(overdue) == 1
    assert overdue[0].detail.startswith(f"{TICKER} · Empréstimo 1")


def test_the_loan_of_the_incorporated_fund_passes_to_the_mother(match):
    sim, ana, bruno, mother_client = match
    daughter = sim.found_fund(bruno, found_request("BORE11"))
    sim.contribute_to_fund(
        bruno, daughter.id, FundContributionRequest(cash=Decimal(5000))
    )
    sim.open_fund_offer(bruno, daughter.id, 20)
    sim.close_fund_offer(bruno, daughter.id)
    book = book_of(sim)
    # A gestão passa à Ana, que passa a gerir as duas e tem cotas da segunda para votar
    held = book.by_id(daughter.id)
    held.terms = held.terms.model_copy(update={"manager_user_id": ana.id})
    sim._engine.broker.receive_position(
        ana.client_id, "BORE11", Decimal(10), Decimal(100)
    )
    daughter_client = held.account.client_id
    sim.contract_loan(ana, daughter_client, Decimal(2000), 12)
    # A incorporadora contrata depois da incorporada: o empréstimo dela é o segundo na ordem do banco
    sim.contract_loan(ana, mother_client, Decimal(1000), 12)
    debt = sim._engine.credit_book.loan_debt(daughter_client, sim._engine.current_date)

    sim.propose_fund_merge(
        ana,
        book.get(TICKER).terms.id,
        FundMergeProposalRequest(daughter_fund_id=daughter.id),
    )
    for _ in range(8):
        if book.is_merged("BORE11"):
            break
        sim.next_tick()

    assert book.is_merged("BORE11")
    credit = sim._engine.credit_book
    assert credit.loans(daughter_client) == []
    assert sim.get_credit(ana, mother_client).loan_debt >= debt
    # A dívida mudou de carteira também no banco
    EventManager.flush()
    portfolio = UserManager.get_portfolio_id(mother_client)
    events = repository.credit.get_events(sim.settings.id, portfolio)
    assert len(credit.loans(mother_client)) == 2
    # A numeração da tela é a de quando a carteira é carregada de novo: a da incorporada vem primeiro
    reloaded = replay(events)
    assert {loan.loan_id: loan.number for loan in credit.loans(mother_client)} == {
        loan.loan_id: loan.number for loan in reloaded.loans.values()
    }
    assert sorted(loan.number for loan in credit.loans(mother_client)) == [1, 2]
