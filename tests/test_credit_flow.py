"""Crédito pelo HTTP com a partida parada: cada operação grava os eventos na hora."""

from __future__ import annotations

from decimal import Decimal

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.enum import CreditEventType
from backend.core.runtime.simulation_manager import SimulationManager
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
