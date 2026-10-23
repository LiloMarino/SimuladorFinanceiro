"""HTTP, transações e retomada com PostgreSQL e motor financeiro reais."""

import uuid
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core import repository
from backend.core.dto.government import GovernmentRulesDTO, PolicyDTO, TermDTO
from backend.core.dto.simulation import SimulationDTO
from backend.core.models.models import EventCashflow, GovernmentEvent
from backend.core.player_colors import PLAYER_COLORS
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.achievements.evaluator import match_result
from backend.features.government.runtime import GovernmentRuntime
from backend.features.simulation.simulation import Simulation
from backend.features.statistics.report import build_overview_report
from backend.routes.government import government_router
from backend.routes.operation import operation_router
from backend.routes.portfolio import portfolio_router
from tests.fakes import simulation_settings


@pytest.fixture
def government_match(market, monkeypatch, request):
    users = [repository.user.create_user(uuid.uuid4(), name) for name in ("Ana", "Bia")]
    monkeypatch.setattr(UserManager, "_active_players", {u.client_id: u for u in users})
    monkeypatch.setattr(
        UserManager, "_client_user_cache", {u.client_id: u for u in users}
    )
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(SimulationManager, "_simulation_id", None)
    monkeypatch.setattr(EventManager, "_events", [])
    monkeypatch.setattr(EventManager, "_touched_users", set())
    monkeypatch.setattr(
        RealtimeBrokerManager,
        "get_broker",
        lambda: SimpleNamespace(notify=lambda *_a, **_kw: None),
    )
    settings = simulation_settings().model_copy(
        update={
            "start_date": date(2003, 10, 7),
            "end_date": date(2008, 10, 7),
            "government": GovernmentRulesDTO(
                enabled=True,
                manual_selic=True,
                ranking=getattr(request, "param", "individual"),
            ),
        }
    )
    sim_id = repository.simulation.create_simulation(settings)
    repository.simulation_player.save(
        sim_id, {u.id: PLAYER_COLORS[i] for i, u in enumerate(users)}
    )
    repository.user.seed_simulation_users(
        sim_id, [u.id for u in users], settings.start_date, settings.starting_cash
    )
    SimulationManager.set_simulation_id(sim_id)
    sim = Simulation(SimulationDTO(id=sim_id, **settings.model_dump()), random_seed=7)
    SimulationManager.register_simulation(sim)
    app = FastAPI()
    for router in (government_router, operation_router, portfolio_router):
        app.include_router(router)
    with TestClient(app) as client:
        client.cookies.set("client_id", str(users[0].client_id))
        yield sim, users, client, market


def request(client, **body):
    result = client.post(
        "/api/government/actions", json={"request_id": str(uuid.uuid4()), **body}
    )
    assert result.status_code == 200, result.text
    return result.json()


def appoint(sim, user_id):
    runtime = sim._government
    state = runtime.state.model_copy(deep=True)
    state.term = TermDTO(
        party_id=1,
        president=user_id,
        start=sim.get_current_date(),
        end=date(2007, 10, 7),
    )
    runtime._save(state, "inauguration")


def test_public_preview_is_read_only_and_presidential_actions_are_authorized(
    government_match,
):
    sim, users, client, engine = government_match
    before = sim._government.state.model_dump()
    cash = sim.get_cash(users[0].client_id)
    result = client.post(
        "/api/government/preview",
        json={
            "action": "propose",
            "kind": "PRODUCT_TARIFF",
            "target": "STEEL",
            "value": "0.1",
        },
    )
    assert result.status_code == 200, result.text
    assert result.json()["as_of"] == "2003-10-07"
    assert len(result.json()["impacts"]) > 0
    assert sim._government.state.model_dump() == before
    assert sim.get_cash(users[0].client_id) == cash
    denied = client.post(
        "/api/government/actions", json={"action": "propose", "value": "0.2"}
    )
    assert denied.status_code == 409
    request(client, action="found", name="Horizonte", acronym="HOR", amount="500")
    appoint(sim, users[0].id)
    request(
        client, action="propose", kind="PRODUCT_TARIFF", target="STEEL", value="0.1"
    )
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(GovernmentEvent)) == 4
    client.cookies.set("client_id", str(users[1].client_id))
    assert (
        client.post(
            "/api/government/actions", json={"action": "withdraw", "policy_id": 1}
        ).status_code
        == 409
    )


def test_runoff_donation_is_atomic_idempotent_and_resumes_without_recharging(
    government_match,
):
    sim, users, client, engine = government_match
    runtime = sim._government
    state = runtime.state.model_copy(deep=True)
    state.processed_on = date(2004, 10, 10)
    state.finalists = [-1, -2]
    runtime._save(state, "runoff")
    sim._current_date = state.processed_on
    sim._engine.current_date = state.processed_on
    before = sim.get_cash(users[0].client_id)
    body = {
        "request_id": str(uuid.uuid4()),
        "action": "donate",
        "party_id": -1,
        "amount": "125.25",
    }
    first = client.post("/api/government/actions", json=body)
    assert first.status_code == 200, first.text
    second = client.post("/api/government/actions", json=body)
    assert second.status_code == 200, second.text
    assert first.json()["state"]["revision"] == second.json()["state"]["revision"]
    assert sim.get_cash(users[0].client_id) == before - Decimal("125.25")
    with Session(engine) as session:
        assert (
            session.scalar(
                select(func.count())
                .select_from(EventCashflow)
                .where(EventCashflow.event_type == "CAMPAIGN")
            )
            == 1
        )
    repository.government.clear_cache()
    restored = GovernmentRuntime(sim, 7)
    assert restored.state == runtime.state
    restored.advance(state.processed_on)
    assert sim.get_cash(users[0].client_id) == before - Decimal("125.25")
    # Falha no lançamento financeiro reverte também o registro político.
    invalid = restored.state.model_copy(deep=True)
    invalid.revision += 1
    with pytest.raises(IntegrityError):
        repository.government.append(
            sim.settings.id, invalid, "donate", users[0].id, {999999: Decimal(10)}
        )
    assert (
        repository.government.states(sim.settings.id)[-1].revision
        == runtime.state.revision
    )
    with Session(engine) as session:
        assert (
            session.scalar(select(func.max(GovernmentEvent.revision)))
            == runtime.state.revision
        )


def test_president_cannot_buy_or_sell_while_paused_and_old_orders_are_cancelled(
    government_match,
):
    sim, users, client, _ = government_match
    request(client, action="found", name="Horizonte", acronym="HOR")
    # Uma compra antes do mandato e outra ordem que fica no book.
    assert (
        client.post(
            "/api/variable-income/BANK_A/orders",
            json={"action": "buy", "type": "market", "quantity": 1},
        ).status_code
        == 200
    )
    limit = client.post(
        "/api/variable-income/BANK_A/orders",
        json={"action": "buy", "type": "limit", "quantity": 1, "limit_price": 0.01},
    )
    assert limit.status_code == 200, limit.text
    appoint(sim, users[0].id)
    for action in ("buy", "sell"):
        denied = client.post(
            "/api/variable-income/BANK_A/orders",
            json={"action": action, "type": "market", "quantity": 1},
        )
        assert denied.status_code == 409, denied.text
    asset = client.get("/api/fixed-income").json()[0]
    assert (
        client.post(
            f"/api/fixed-income/{asset['asset_uuid']}/buy", json={"quantity": "100"}
        ).status_code
        == 409
    )
    sim.next_tick()
    assert not [
        o
        for o in sim._engine.matching_engine.order_book._orders_by_id.values()
        if o.client_id == users[0].client_id
    ]
    public = client.get("/api/government").json()
    assert public["trading_frozen"] and public["president_portfolio"]["BANK_A"] == 1
    assert public["president_finances"]["total_networth"]
    client.cookies.set("client_id", str(users[1].client_id))
    assert (
        client.post(
            "/api/variable-income/BANK_A/orders",
            json={"action": "buy", "type": "market", "quantity": 1},
        ).status_code
        == 200
    )
    assert sim.get_speed() == 0


def test_quotes_history_portfolio_and_tax_preview_share_the_effective_policy(
    government_match,
):
    sim, _users, client, _ = government_match
    runtime = sim._government
    state = runtime.state.model_copy(deep=True)
    state.policies = [
        PolicyDTO(
            id=1,
            kind="PUBLIC_SPENDING",
            value=Decimal(100_000_000),
            proposed_on=sim.get_current_date() - timedelta(days=120),
            author=1,
            party_id=1,
            status="approved",
            effective_on=sim.get_current_date() - timedelta(days=31),
            position=4,
        ),
        PolicyDTO(
            id=2,
            kind="STOCK_EXEMPTION",
            value=Decimal(5000),
            proposed_on=sim.get_current_date() - timedelta(days=120),
            author=1,
            party_id=1,
            status="approved",
            effective_on=sim.get_current_date(),
            position=4,
        ),
    ]
    runtime._save(state, "policies")
    sim._price_impact.refresh(sim.get_current_date())
    sim._engine.update_market_data(sim.get_stocks())
    quote = client.get("/api/variable-income/BANK_A").json()
    impacts = client.get("/api/government").json()["impacts"]
    effect = next(i for i in impacts if i["ticker"] == "BANK_A")
    assert quote["close"] == pytest.approx(effect["effective_price"])
    preview = client.post(
        "/api/variable-income/BANK_A/order-preview",
        json={"action": "buy", "quantity": 1},
    ).json()
    assert Decimal(preview["stock_sales_exemption"]) == 5000
    portfolio = client.get("/api/portfolio").json()
    assert Decimal(portfolio["stock_sales_exemption"]) == 5000
    assert any(row.ticker == "BANK_A" for row in sim.get_market())


def test_manual_selic_reprices_the_book_and_preview_without_a_tick(government_match):
    sim, users, client, _ = government_match
    appoint(sim, users[0].id)
    view = client.get("/api/government").json()
    before = client.get("/api/variable-income/BANK_A").json()["close"]
    history_length = len(sim._engine.matching_engine.market_data.get_recent("BANK_A"))
    target = Decimal(str(view["current_selic"])) + Decimal("0.005")
    request(client, action="selic", value=str(target))
    client.cookies.set("client_id", str(users[1].client_id))
    quote = client.get("/api/variable-income/BANK_A").json()["close"]
    preview = client.post(
        "/api/variable-income/BANK_A/order-preview",
        json={"action": "buy", "quantity": 1},
    ).json()
    assert quote < before
    current = sim._engine.matching_engine.market_data.get_last("BANK_A")
    assert current is not None and current.close == quote
    assert (
        len(sim._engine.matching_engine.market_data.get_recent("BANK_A"))
        == history_length
    )
    ask = sim._engine.matching_engine.order_book.best_sell("BANK_A")
    assert ask is not None and Decimal(preview["price"]) == Decimal(
        str(ask.price)
    ).quantize(Decimal("0.01"))
    order = client.post(
        "/api/variable-income/BANK_A/orders",
        json={"action": "buy", "type": "market", "quantity": 1},
    )
    assert order.status_code == 200 and order.json()["status"] == "EXECUTED"
    trades = client.get("/api/variable-income/BANK_A/trades").json()
    assert Decimal(str(trades[-1]["price"])) == Decimal(preview["price"])
    assert sim.get_speed() == 0 and sim.get_current_date() == date(2003, 10, 7)


def test_shared_public_view_is_cached_but_presidential_permissions_are_per_player(
    government_match,
):
    sim, users, client, engine = government_match
    appoint(sim, users[0].id)
    first = client.get("/api/government").json()
    statements = []

    def count(_conn, _cursor, statement, _parameters, _context, _executemany):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", count)
    try:
        client.cookies.set("client_id", str(users[1].client_id))
        other = client.get("/api/government").json()
        assert not statements
    finally:
        event.remove(engine, "before_cursor_execute", count)
    assert first["can_govern"] and first["trading_frozen"]
    assert not other["can_govern"] and not other["trading_frozen"]
    assert first["state"] == other["state"] and first["my_id"] != other["my_id"]


@pytest.mark.parametrize("government_match", ["parties"], indirect=True)
def test_party_victory_sums_member_wealth_and_awards_all_winning_members(
    government_match,
):
    sim, users, client, _ = government_match
    request(client, action="found", name="Horizonte", acronym="HOR")
    client.cookies.set("client_id", str(users[1].client_id))
    request(client, action="join", party_id=1)
    report = build_overview_report([sim.settings.id])
    assert report.party_ranking_decides
    assert report.parties[0].networth == sum(
        (p.total_networth for p in report.players), Decimal(0)
    )
    assert set(report.parties[0].members) == {"Ana", "Bia"}
    assert match_result(sim.settings.id, users, False).winners == frozenset(
        u.id for u in users
    )
