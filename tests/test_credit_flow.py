"""Crédito pelo HTTP com a partida parada: cada operação grava os eventos na hora."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.enum import CreditEventType
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.realtime.schemas import CreditInstallmentPaidEventDTO
from backend.features.simulation import feed_support
from backend.routes.credit import credit_router
from tests.test_paused_trading import paused_match  # noqa: F401


def test_contract_prepay_and_payoff_while_paused(paused_match):  # noqa: F811
    sim, users, _ = paused_match
    user = users[0]
    cash_before = sim.get_cash(user.client_id)
    app = FastAPI()
    app.include_router(credit_router)

    with TestClient(app) as http:
        http.cookies.set("client_id", str(user.client_id))
        overview = http.get("/api/credit")
        assert overview.status_code == 200, overview.text
        assert overview.json()["rating"]["grade"] == "AAA"
        assert overview.json()["loans"] == []

        quote = http.get(
            "/api/credit/quote", params={"amount": 5000, "term_months": 24}
        )
        assert quote.status_code == 200, quote.text
        installment = Decimal(quote.json()["installment"])

        too_much = http.post(
            "/api/credit/loans", json={"amount": "999999", "term_months": 24}
        )
        assert too_much.status_code == 409

        created = http.post(
            "/api/credit/loans", json={"amount": "5000", "term_months": 24}
        )
        assert created.status_code == 204, created.text
        assert sim.get_cash(user.client_id) == cash_before + 5000
        # O evento já está no banco: a partida segue parada
        events = repository.credit.get_events(
            SimulationManager.get_active_simulation_id(), user.id
        )
        assert [e.event_type for e in events] == [CreditEventType.CONTRACT]

        loans = http.get("/api/credit").json()["loans"]
        assert len(loans) == 1
        assert Decimal(loans[0]["installment"]) == installment
        loan_id = loans[0]["id"]

        preview = http.get(
            f"/api/credit/loans/{loan_id}/prepayment", params={"amount": 1000}
        )
        assert preview.status_code == 200, preview.text
        assert Decimal(preview.json()["shorten_term"]["interest_saved"]) > 0

        prepaid = http.post(
            f"/api/credit/loans/{loan_id}/prepayment",
            json={"amount": "1000", "mode": "SHORTEN_TERM"},
        )
        assert prepaid.status_code == 204, prepaid.text
        assert sim.get_cash(user.client_id) == cash_before + 4000

        paid_off = http.post(f"/api/credit/loans/{loan_id}/payoff")
        assert paid_off.status_code == 204, paid_off.text
        assert http.get("/api/credit").json()["loans"] == []
        assert http.post(f"/api/credit/loans/{loan_id}/payoff").status_code == 404


def listen(
    monkeypatch: pytest.MonkeyPatch, *clients: UUID
) -> list[tuple[str, UUID | None]]:
    """Os clientes assinam o panorama e as pendências; devolve o que o servidor entregou."""
    sent: list[tuple[str, UUID | None]] = []
    monkeypatch.setattr(
        feed_support,
        "subscribed_clients",
        lambda event: (
            set(clients) if event in ("credit_update", "pending_update") else set()
        ),
    )
    monkeypatch.setattr(
        feed_support,
        "notify",
        lambda event, _payload, to=None: sent.append((event, to)),
    )
    return sent


def test_each_credit_operation_sends_the_overview_and_the_pending_to_who_sees_the_account(
    paused_match,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
):
    _sim, users, _ = paused_match
    ana, bia = users
    sent = listen(monkeypatch, ana.client_id, bia.client_id)
    app = FastAPI()
    app.include_router(credit_router)

    with TestClient(app) as http:
        http.cookies.set("client_id", str(ana.client_id))
        assert (
            http.post(
                "/api/credit/loans", json={"amount": "5000", "term_months": 24}
            ).status_code
            == 204
        )
        assert sorted(sent) == sorted(
            [("credit_update", ana.client_id), ("pending_update", ana.client_id)]
        )

        sent.clear()
        [loan] = http.get("/api/credit").json()["loans"]
        assert http.post(f"/api/credit/loans/{loan['id']}/payoff").status_code == 204
        assert ("credit_update", ana.client_id) in sent
        assert all(to == ana.client_id for _, to in sent)


def test_every_credit_notice_marks_the_account_for_the_overview(
    paused_match,  # noqa: F811
):
    sim, users, _ = paused_match
    ana = users[0]
    book = sim._engine.credit_book
    changed: list[UUID] = []
    book.on_changed = changed.append

    book._notify(
        "credit_installment_paid",
        CreditInstallmentPaidEventDTO(
            loan_number=1, installment_number=1, total_installments=2, amount=Decimal(1)
        ),
        ana.client_id,
    )

    assert changed == [ana.client_id]


def test_the_loan_read_back_from_the_database_has_the_state_of_the_live_one(
    paused_match,  # noqa: F811
):
    sim, users, _ = paused_match
    ana = users[0]
    book = sim._engine.credit_book
    live = book.contract(ana.client_id, Decimal(5000), 24)
    EventManager.flush()

    # Sem o estado em memória, o livro refaz o empréstimo dos eventos gravados
    book.forget(ana.client_id)
    [back] = book.loans(ana.client_id)

    assert back.annual_rate == live.annual_rate
    assert back.state.installment == live.state.installment
    live_state, back_state = live.state, back.state
    for _ in range(12):
        live_state, back_state = live_state.advance(), back_state.advance()
    assert back_state.cycle_balance == live_state.cycle_balance
