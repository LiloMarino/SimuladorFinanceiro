"""O fluxo do gestor pela fachada da partida, com banco: fundar, integralizar, abrir a oferta e mudar as taxas."""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.fund import (
    FundContributionRequest,
    FundContributionStockRequest,
    FundFeesRequest,
    FundFoundRequest,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import AssetClass, EquityEventType, OrderAction
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.funds.fund_book import FundBook
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.variable_income.entities.order import MarketOrder
from tests.test_fund_simulation import TICKER, empty_match
from tests.test_simulation_loader import started  # noqa: F401


def found_request(ticker: str = TICKER) -> FundFoundRequest:
    return FundFoundRequest(
        name="Aura",
        ticker=ticker,
        management_fee=Decimal("0.01"),
        performance_fee=Decimal("0.10"),
    )


@pytest.fixture
def flow(started) -> tuple[Simulation, UserDTO]:  # noqa: F811
    return empty_match()


def test_founding_creates_a_fund_without_quotas(flow):
    sim, ana = flow

    fund = sim.found_fund(ana, found_request())

    assert fund.ticker == TICKER
    assert fund.quotas == 0
    assert [f.ticker for f in sim.get_funds()] == [TICKER]
    assert sim.get_fund(fund.id).days == []


def test_founding_the_same_ticker_twice_is_a_conflict(flow):
    sim, ana = flow
    sim.found_fund(ana, found_request())

    with pytest.raises(ConflictError):
        sim.found_fund(ana, found_request())


def test_imported_asset_ticker_is_not_claimed(flow):
    repository.stock.add_stock("ABCD11", "Importado", AssetClass.STOCK)

    assert repository.fund.claim_stock("ABCD11", "Aura", 1) is None


def test_quota_of_another_founder_is_not_claimed_but_the_founder_gets_the_same_row(
    flow,
):
    sim, ana = flow
    fund = sim.found_fund(ana, found_request())

    assert repository.fund.claim_stock(TICKER, "Aura", ana.id + 1) is None
    reclaimed = repository.fund.claim_stock(TICKER, "Aura", ana.id)
    assert reclaimed is not None
    assert reclaimed.id == book_of(sim).get(TICKER).terms.stock_id
    assert fund.ticker == TICKER


def test_cash_contribution_moves_the_money_and_issues_quotas_to_the_manager(flow):
    sim, ana = flow
    fund = sim.found_fund(ana, found_request())
    cash_before = sim._engine.get_cash(ana.client_id)

    response = sim.contribute_to_fund(
        ana, fund.id, FundContributionRequest(cash=Decimal(5000))
    )

    assert response.quotas == 50  # R$ 100 por cota na primeira integralização
    assert sim._engine.get_cash(ana.client_id) == cash_before - 5000
    held = sim._engine.broker.get_positions(ana.client_id)[TICKER]
    assert held.size == 50
    assert sim.get_fund(fund.id).quotas == 50


def test_only_the_manager_contributes(flow):
    sim, ana = flow
    fund = sim.found_fund(ana, found_request())
    stranger = ana.model_copy(update={"id": ana.id + 1})

    with pytest.raises(Exception, match="gestor"):
        sim.contribute_to_fund(
            stranger, fund.id, FundContributionRequest(cash=Decimal(100))
        )


def test_offer_opens_once_and_closes_the_contributions(flow):
    sim, ana = flow
    fund = sim.found_fund(ana, found_request())
    sim.contribute_to_fund(ana, fund.id, FundContributionRequest(cash=Decimal(5000)))

    opened = sim.open_fund_offer(ana, fund.id, 20)

    assert opened.listed_on is not None
    assert opened.offer_remaining == 20
    with pytest.raises(ConflictError, match="uma vez só"):
        sim.open_fund_offer(ana, fund.id, 20)
    with pytest.raises(ConflictError, match="antes da oferta"):
        sim.contribute_to_fund(ana, fund.id, FundContributionRequest(cash=Decimal(500)))


def test_offer_without_contribution_is_refused(flow):
    sim, ana = flow
    fund = sim.found_fund(ana, found_request())

    with pytest.raises(ConflictError, match="Integralize"):
        sim.open_fund_offer(ana, fund.id, 20)


def test_closing_the_offer_stops_the_sale(flow):
    sim, ana = flow
    fund = sim.found_fund(ana, found_request())
    sim.contribute_to_fund(ana, fund.id, FundContributionRequest(cash=Decimal(5000)))
    sim.open_fund_offer(ana, fund.id, 20)

    sim.close_fund_offer(ana, fund.id)

    assert sim.get_fund(fund.id).offer_remaining in (None, 0)
    with pytest.raises(ConflictError, match="não tem oferta"):
        sim.close_fund_offer(ana, fund.id)


def test_new_fees_are_saved_as_pending_until_the_next_month(flow):
    sim, ana = flow
    fund = sim.found_fund(ana, found_request())

    changed = sim.set_fund_fees(
        ana,
        fund.id,
        FundFeesRequest(
            management_fee=Decimal("0.02"), performance_fee=Decimal("0.20")
        ),
    )

    assert changed.management_fee == Decimal("0.01")
    assert changed.pending_management_fee == Decimal("0.02")
    [saved] = repository.fund.of_simulation(sim.settings.id)
    assert saved.pending_management_fee == Decimal("0.02")
    assert saved.pending_from is not None


def book_of(sim: Simulation) -> FundBook:
    assert sim._funds is not None
    return sim._funds


def player(sim: Simulation, nickname: str) -> UserDTO:
    return next(
        u
        for u in repository.simulation_player.participants(sim.settings.id)
        if u.nickname == nickname
    )


def buy_at_market(sim: Simulation, user: UserDTO, ticker: str, size: int) -> None:
    """Compra a mercado e roda o pregão que executa a ordem."""
    sim._engine.matching_engine.submit(
        MarketOrder(
            client_id=user.client_id,
            ticker=ticker,
            size=Decimal(size),
            action=OrderAction.BUY,
            placed_on=sim._current_date,
        )
    )
    sim.next_tick()


def fund_with_cash(sim: Simulation, ana: UserDTO) -> int:
    """A gestora da Ana com 5.000 integralizados em caixa (50 cotas ao PL de R$ 100)."""
    fund = sim.found_fund(ana, found_request())
    sim.contribute_to_fund(ana, fund.id, FundContributionRequest(cash=Decimal(5000)))
    return fund.id


def test_second_player_buys_the_offer_and_the_cash_reaches_the_fund(started):  # noqa: F811
    sim, ana = empty_match("Bruno")
    bruno = player(sim, "Bruno")
    fund_id = fund_with_cash(sim, ana)
    sim.open_fund_offer(ana, fund_id, 20)
    fund = book_of(sim).get(TICKER)
    fund_cash = sim._engine.get_cash(fund.account.client_id)
    bruno_cash = sim._engine.get_cash(bruno.client_id)

    buy_at_market(sim, bruno, TICKER, 5)

    held = sim._engine.broker.get_positions(bruno.client_id)[TICKER]
    assert held.size == 5
    paid = bruno_cash - sim._engine.get_cash(bruno.client_id)
    assert paid > 0
    # O dinheiro da oferta vai inteiro para a conta da gestora
    assert sim._engine.get_cash(fund.account.client_id) == fund_cash + paid
    assert fund.account.offer_remaining == 15
    assert sim.get_fund(fund_id).offer_remaining == 15


def test_ranking_counts_the_quotas_once_and_keeps_the_fund_out_as_a_player(started):  # noqa: F811
    sim, ana = empty_match()
    fund_id = fund_with_cash(sim, ana)
    sim.open_fund_offer(ana, fund_id, 20)
    fund = book_of(sim).get(TICKER)
    sim.next_tick()

    # A cota do gestor vale o preço de ranking, e a carteira da gestora não entra na conta dele
    balance = sim._engine.balance_sheet(ana.client_id)
    ranking_price = sim._engine.ranking_prices[TICKER]
    assert balance.equity_by_class[AssetClass.FUND] == 50 * ranking_price
    assert balance.total_equity == 50 * ranking_price

    # A taxa de administração sai do caixa da gestora e entra no do gestor
    ana_cash = sim._engine.get_cash(ana.client_id)
    fund_cash = sim._engine.get_cash(fund.account.client_id)
    book_of(sim).on_month(sim._current_date)
    EventManager.flush()
    received = sim._engine.get_cash(ana.client_id) - ana_cash
    assert received > 0
    assert sim._engine.get_cash(fund.account.client_id) == fund_cash - received

    # A gestora não é jogador: sem carteira de usuário, sem snapshot e sem linha no ranking
    assert set(repository.portfolio.ids(sim.settings.id)) == {ana.id}
    history = repository.statistics.get_players_history([sim.settings.id])
    assert [h.player_nickname for h in history] == ["Ana"]
    last = history[0].history[-1]
    assert last.total_equity == 50 * ranking_price
    assert last.total_networth == last.total_equity + last.total_cash


def test_stock_contribution_is_a_transfer_without_sale_or_darf(flow):
    sim, ana = flow
    buy_at_market(sim, ana, "BANK_A", 40)
    cost = sim._engine.broker.get_positions(ana.client_id)["BANK_A"]
    average_price = cost.avg_price
    fund = sim.found_fund(ana, found_request())

    response = sim.contribute_to_fund(
        ana,
        fund.id,
        FundContributionRequest(
            stocks=[FundContributionStockRequest(ticker="BANK_A", quantity=Decimal(40))]
        ),
    )

    assert response.quotas > 0
    assert "BANK_A" not in sim._engine.broker.get_positions(ana.client_id)
    held = sim._engine.broker.get_positions(book_of(sim).get(TICKER).account.client_id)[
        "BANK_A"
    ]
    assert held.size == 40
    # O custo médio acompanha as ações até a gestora
    assert held.avg_price == average_price
    portfolio_id = SimulationManager.get_portfolio_id(ana.id)
    events = repository.portfolio.get_equity_events(portfolio_id)
    assert [e.event_type for e in events if e.ticker == "BANK_A"] == [
        EquityEventType.BUY,
        EquityEventType.TRANSFER_OUT,
    ]
    months = sim._engine.assess_income_tax(portfolio_id)
    assert all(m.stock_sales == 0 and m.darf_amount is None for m in months)


def test_saved_fund_resumes_with_the_maker_state_and_the_pending_fees(flow, started):  # noqa: F811
    sim, ana = flow
    buy_at_market(sim, ana, "BANK_A", 40)
    fund = sim.found_fund(ana, found_request())
    sim.contribute_to_fund(
        ana,
        fund.id,
        FundContributionRequest(
            cash=Decimal(3000),
            stocks=[
                FundContributionStockRequest(ticker="BANK_A", quantity=Decimal(40))
            ],
        ),
    )
    sim.open_fund_offer(ana, fund.id, 20)
    sim.set_fund_fees(
        ana,
        fund.id,
        FundFeesRequest(
            management_fee=Decimal("0.02"), performance_fee=Decimal("0.20")
        ),
    )
    sim.next_tick()
    before = book_of(sim).get(TICKER)
    summary = repository.simulation.get_simulation(sim.settings.id)
    assert summary is not None

    SimulationLoader.load(summary)

    resumed = SimulationManager.get_active_simulation()
    after = book_of(resumed).get(TICKER)
    assert after.account.quotas == before.account.quotas
    assert after.account.maker_quotas == before.account.maker_quotas
    assert round(after.account.maker_cash, 6) == round(before.account.maker_cash, 6)
    assert after.account.offer_remaining == before.account.offer_remaining
    assert after.terms.pending_management_fee == Decimal("0.02")
    assert after.terms.pending_performance_fee == Decimal("0.20")
    assert after.terms.pending_from == before.terms.pending_from
    held = resumed._engine.broker.get_positions(after.account.client_id)["BANK_A"]
    assert held.size == 40
