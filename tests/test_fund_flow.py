"""O fluxo do gestor pela fachada da partida, com banco: fundar, integralizar, abrir a oferta e mudar as taxas."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from backend.core import repository
from backend.core.dto.fund import (
    FundContributionRequest,
    FundContributionStockRequest,
    FundFeesRequest,
    FundFoundRequest,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import AssetClass, EquityEventType, OrderAction, OrderStatus
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.funds.fund_book import FundBook
from backend.features.government.measures import short_date
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.variable_income.entities.order import (
    MARKET_CLIENT_ID,
    LimitOrder,
    MarketOrder,
)
from tests.fakes import simulation_settings
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
    assert sim.get_fund(ana, fund.id).series == []


def test_founding_the_same_ticker_twice_is_a_conflict(flow):
    sim, ana = flow
    sim.found_fund(ana, found_request())

    with pytest.raises(ConflictError):
        sim.found_fund(ana, found_request())


def test_ticker_with_the_letters_of_an_imported_asset_is_not_claimed(flow):
    repository.stock.add_stock("PETR4", "Importado", AssetClass.STOCK)

    assert repository.fund.claim_stock("PETR11", "Aura") is None
    assert repository.fund.claim_stock("PETS11", "Aura") is not None


def test_quota_row_is_shared_by_the_funds_with_the_same_ticker(flow):
    """O ticker é uma linha global: outra partida, ou outro fundador, reusa a mesma cota."""
    sim, ana = flow
    fund = sim.found_fund(ana, found_request())

    reclaimed = repository.fund.claim_stock(TICKER, "Outra gestora")

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
    assert sim.get_fund(ana, fund.id).quotas == 50


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

    assert sim.get_fund(ana, fund.id).offer_remaining in (None, 0)
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
    assert sim.get_fund(ana, fund_id).offer_remaining == 15


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


def test_accounts_list_the_personal_one_first_and_only_the_funds_the_player_runs(
    started,  # noqa: F811
):
    sim, ana = empty_match("Bruno")
    bruno = player(sim, "Bruno")
    sim.found_fund(bruno, found_request("ZETA11"))
    fund_id = fund_with_cash(sim, ana)

    accounts = sim.get_fund_accounts(ana)

    personal, managed = accounts
    assert (personal.fund_id, personal.ticker) == (None, None)
    assert personal.cash == sim._engine.get_cash(ana.client_id)
    assert (managed.fund_id, managed.ticker, managed.name) == (fund_id, TICKER, "Aura")
    assert managed.cash == Decimal(5000)
    assert managed.frozen_until is None and personal.frozen_until is None
    assert sim.get_fund_accounts(bruno)[0].fund_id is None
    assert len(sim.get_fund_accounts(bruno)) == 2


def test_ticker_check_tells_free_format_asset_and_fund_without_changing_anything(
    started,  # noqa: F811
):
    sim, ana = empty_match("Bruno")
    bruno = player(sim, "Bruno")
    repository.stock.add_stock("PETR3", "Importado", AssetClass.STOCK)
    repository.stock.add_stock("PETR4", "Importado", AssetClass.STOCK)
    repository.stock.add_stock("KNRI11", "Importado", AssetClass.FII)
    sim.found_fund(ana, found_request())

    def check(ticker: str, user: UserDTO = bruno) -> tuple[str, str | None]:
        result = sim.check_fund_ticker(user, ticker)
        return result.status, result.owner_name

    assert check("ZETA11") == ("free", None)
    assert check("ZETA1") == ("format", None)
    assert check("zeta11") == ("format", None)
    assert check("PETR11") == ("asset", None)
    assert check("KNRI11") == ("asset", None)
    assert check(TICKER) == ("fund", "Ana")
    assert check(TICKER, ana) == ("free", None)
    assert [f.ticker for f in sim.get_funds()] == [TICKER]


def test_ticker_check_ignores_the_fund_of_a_founder_in_another_match(
    started,  # noqa: F811
):
    """A sigla é conferida só contra a partida: gestora de outro jogador em outra partida não conflita."""
    sim, ana = empty_match("Bruno")
    bruno = player(sim, "Bruno")
    stock = repository.fund.claim_stock("OMEG11", "Omega")
    assert stock is not None
    other_match = repository.simulation.create_simulation(
        simulation_settings().model_copy(
            update={"name": "Outra", "funds_enabled": True}
        )
    )
    repository.fund.create(
        simulation_id=other_match,
        stock_id=stock.id,
        ticker="OMEG11",
        client_id=uuid4(),
        founder_user_id=ana.id,
        manager_user_id=ana.id,
        name="Omega",
        management_fee=Decimal("0.01"),
        performance_fee=Decimal("0.10"),
    )

    assert sim.check_fund_ticker(bruno, "OMEG11").status == "free"
    founded = sim.found_fund(bruno, found_request("OMEG11"))
    assert founded.ticker == "OMEG11"
    assert sim.check_fund_ticker(ana, "OMEG11").status == "fund"


def test_offer_sold_out_is_closed_in_the_facade(flow):
    sim, ana = flow
    fund_id = fund_with_cash(sim, ana)
    sim.open_fund_offer(ana, fund_id, 20)
    book_of(sim).by_id(fund_id).account.issue(Decimal(20))

    summary = sim.get_fund(ana, fund_id)

    assert (summary.offer_session, summary.offer_ends_on) == (None, None)
    with pytest.raises(ConflictError, match="não tem oferta"):
        sim.close_fund_offer(ana, fund_id)
    with pytest.raises(ConflictError, match="uma vez só"):
        sim.open_fund_offer(ana, fund_id, 20)


def governing(sim: Simulation, president: UserDTO, term_end: date) -> dict:
    """Põe um governo de mentira em que `president` governa até `term_end`; trocar a chave `on` termina o mandato."""
    state = {"on": True}
    sim._government = SimpleNamespace(  # type: ignore[assignment]
        president=lambda: president if state["on"] else None,
        term_end=lambda: term_end,
        ensure_can_trade=lambda _client_id: None,
    )
    return state


def test_taking_office_freezes_the_managers_fund_until_the_term_ends(flow):
    sim, ana = flow
    fund_id = fund_with_cash(sim, ana)
    fund_client = book_of(sim).by_id(fund_id).account.client_id
    term_end = date(2004, 12, 31)
    resting = LimitOrder(
        client_id=fund_client,
        ticker=TICKER,
        size=Decimal(1),
        action=OrderAction.BUY,
        placed_on=sim._current_date,
        price=1.0,
    )
    sim._engine.matching_engine.submit(resting)
    state = governing(sim, ana, term_end)
    back_on = short_date(term_end + timedelta(days=1))
    message = f"A gestora está congelada enquanto o gestor governa: ela volta a operar em {back_on}."

    sim._take_office(ana, sim._current_date)

    assert sim._engine.matching_engine.order_book.orders_of(fund_client) == []
    order = MarketOrder(
        client_id=fund_client,
        ticker=TICKER,
        size=Decimal(1),
        action=OrderAction.SELL,
        placed_on=sim._current_date,
    )
    with pytest.raises(ConflictError) as refused:
        sim.create_order(order)
    assert refused.value.detail == message
    with pytest.raises(ConflictError, match="congelada"):
        sim.cancel_order(order_id="qualquer", client_id=fund_client)
    with pytest.raises(ConflictError, match="congelada"):
        sim._ensure_can_operate(fund_client)
    with pytest.raises(ConflictError, match="congelada"):
        sim.contribute_to_fund(ana, fund_id, FundContributionRequest(cash=Decimal(100)))
    with pytest.raises(ConflictError, match="congelada"):
        sim.open_fund_offer(ana, fund_id, 10)
    with pytest.raises(ConflictError, match="congelada"):
        sim.set_fund_fees(
            ana,
            fund_id,
            FundFeesRequest(
                management_fee=Decimal("0.02"), performance_fee=Decimal("0.20")
            ),
        )
    # Ler a conta segue valendo, e o DTO e a lista de contas dizem até quando congela
    assert sim.acting_client(ana.client_id, fund_id) == fund_client
    assert sim.get_fund(ana, fund_id).frozen_until == term_end
    fund_account = sim.get_fund_accounts(ana)[1]
    assert fund_account.frozen_until == term_end
    assert sim.get_fund_accounts(ana)[0].frozen_until == term_end

    state["on"] = False

    assert sim.get_fund(ana, fund_id).frozen_until is None
    sim.open_fund_offer(ana, fund_id, 10)


def test_a_fund_of_someone_else_keeps_operating_while_the_manager_governs(started):  # noqa: F811
    sim, ana = empty_match("Bruno")
    bruno = player(sim, "Bruno")
    bruno_fund = sim.found_fund(bruno, found_request("ZETA11"))
    governing(sim, ana, date(2004, 12, 31))

    sim._take_office(ana, sim._current_date)

    assert sim.get_fund(bruno, bruno_fund.id).frozen_until is None
    sim._ensure_can_operate(book_of(sim).by_id(bruno_fund.id).account.client_id)


def offered_match() -> tuple[Simulation, UserDTO, UserDTO, int]:
    """Ana gere a gestora (50 cotas, oferta de 20 aberta) e o Bruno comprou 5 da oferta."""
    sim, ana = empty_match("Bruno")
    bruno = player(sim, "Bruno")
    fund_id = fund_with_cash(sim, ana)
    sim.open_fund_offer(ana, fund_id, 20)
    buy_at_market(sim, bruno, TICKER, 5)
    return sim, ana, bruno, fund_id


def buy_for_fund(sim: Simulation, fund_id: int, ticker: str, size: int) -> None:
    """A gestora compra ações com o caixa dela."""
    fund = book_of(sim).by_id(fund_id)
    sim._engine.matching_engine.submit(
        MarketOrder(
            client_id=fund.account.client_id,
            ticker=ticker,
            size=Decimal(size),
            action=OrderAction.BUY,
            placed_on=sim._current_date,
        )
    )


def run_days(sim: Simulation, days: int) -> None:
    for _ in range(days):
        sim.next_tick()


def test_list_shows_the_last_trade_price_and_the_manager_nickname(started):  # noqa: F811
    sim, ana = empty_match("Bruno")
    bruno = player(sim, "Bruno")
    fund_id = fund_with_cash(sim, ana)
    sim.open_fund_offer(ana, fund_id, 20)

    [before] = sim.get_funds()
    buy_at_market(sim, bruno, TICKER, 5)
    [after] = sim.get_funds()

    assert (before.price, before.manager_nickname) == (None, "Ana")
    assert after.price == Decimal(100)
    assert after.price is not None
    assert after.nav is not None
    assert after.price / after.nav - 1 == 0


def test_holders_are_listed_from_the_largest_with_color_and_share(started):  # noqa: F811
    sim, ana, bruno, fund_id = offered_match()

    page = sim.get_fund(bruno, fund_id)

    assert [(h.kind, h.nickname, h.quotas, h.color) for h in page.holders] == [
        ("player", "Ana", 50, "chart-1"),
        ("maker", "Formador de mercado", 7, None),
        ("player", "Bruno", 5, "chart-2"),
    ]
    assert page.holders[0].user_id == ana.id
    assert page.holders[1].user_id is None
    assert sum(h.share for h in page.holders) == 1
    assert page.holders[0].share == Decimal(50) / 62


def test_control_is_half_plus_one_and_the_manager_alone_sees_what_he_can_sell(
    started,  # noqa: F811
):
    sim, ana, bruno, fund_id = offered_match()

    as_manager = sim.get_fund(ana, fund_id)
    as_other = sim.get_fund(bruno, fund_id)

    # 62 cotas em circulação: o controle começa em 32 e a Ana, com 50, vende 18
    assert as_manager.control_quotas == as_other.control_quotas == 32
    assert as_manager.sellable_keeping_control == 18
    assert as_other.sellable_keeping_control is None


def test_live_portfolio_is_the_managers_and_the_composition_is_the_rooms(started):  # noqa: F811
    sim, ana, bruno, fund_id = offered_match()
    stock = next(
        ticker
        for ticker, asset in sim._engine.stocks.items()
        if asset.asset_class == AssetClass.STOCK
    )
    buy_for_fund(sim, fund_id, stock, 10)
    sim.next_tick()

    as_manager = sim.get_fund(ana, fund_id)
    as_other = sim.get_fund(bruno, fund_id)

    assert as_other.positions is None
    assert as_manager.positions is not None
    assert [p.asset_class for p in as_manager.positions] == ["cash", "stocks"]
    bought = as_manager.positions[1]
    assert (bought.ticker, bought.quantity) == (stock, 10)
    assert [c.asset_class for c in as_other.composition] == [
        "cash",
        "stocks",
        "fixed_income",
        "treasury",
    ]
    assert as_other.composition == as_manager.composition
    assert sum(c.fraction for c in as_other.composition) == 1
    stocks_class = as_other.composition[1]
    assert stocks_class.value == bought.value
    assert [p.value for p in as_manager.positions] == [
        c.value for c in as_manager.composition if c.value
    ]


def test_offer_in_progress_shows_sold_raised_and_buyers(started):  # noqa: F811
    sim, _ana, bruno, fund_id = offered_match()

    page = sim.get_fund(bruno, fund_id)

    assert (page.offer_sold, page.offer_raised) == (5, 500)
    assert page.offer_buyers is not None
    [buyer] = page.offer_buyers
    assert (buyer.kind, buyer.user_id, buyer.nickname) == ("player", bruno.id, "Bruno")
    assert (buyer.quotas, buyer.color) == (5, "chart-2")


def test_closed_offer_has_no_progress_and_leaves_its_marks_in_the_movements(started):  # noqa: F811
    sim, ana, _bruno, fund_id = offered_match()
    sim.close_fund_offer(ana, fund_id)

    page = sim.get_fund(ana, fund_id)

    assert (page.offer_sold, page.offer_raised, page.offer_buyers) == (None,) * 3
    closed = next(m for m in page.movements if m.type == "offer_closed")
    assert (closed.quotas, closed.amount, closed.price) == (5, 500, 100)
    opened = next(m for m in page.movements if m.type == "offer_opened")
    assert (opened.price, opened.quotas) == (100, 20)
    assert opened.day < closed.day == sim._current_date
    assert page.offer_closed_on == sim._current_date


def test_offer_that_ran_its_course_keeps_what_was_offered_and_closes_on_the_last_session(
    started,  # noqa: F811
):
    sim, ana, _bruno, fund_id = offered_match()
    run_days(sim, 8)

    page = sim.get_fund(ana, fund_id)

    opened = next(m for m in page.movements if m.type == "offer_opened")
    closed = next(m for m in page.movements if m.type == "offer_closed")
    assert (opened.quotas, closed.quotas) == (20, 5)
    assert closed.day == page.offer_closed_on == date(2004, 3, 8)


def test_a_player_trade_with_the_day_and_value_of_an_offer_sale_is_not_a_buyer(
    started,  # noqa: F811
):
    sim, ana = empty_match("Bruno", "Caio")
    bruno = player(sim, "Bruno")
    caio = player(sim, "Caio")
    fund_id = fund_with_cash(sim, ana)
    sim.open_fund_offer(ana, fund_id, 20)
    engine = sim._engine.matching_engine
    day = sim._current_date

    # O Bruno leva 5 cotas da oferta a R$ 100 (R$ 500); no mesmo dia a Ana vende 10 cotas
    # a R$ 50 (R$ 500) à Caio
    engine.submit(
        MarketOrder(
            client_id=bruno.client_id,
            ticker=TICKER,
            size=Decimal(5),
            action=OrderAction.BUY,
            placed_on=day,
        )
    )
    engine.submit(
        LimitOrder(
            client_id=ana.client_id,
            ticker=TICKER,
            size=Decimal(10),
            action=OrderAction.SELL,
            placed_on=day,
            price=50.0,
        )
    )
    engine.submit(
        MarketOrder(
            client_id=caio.client_id,
            ticker=TICKER,
            size=Decimal(10),
            action=OrderAction.BUY,
            placed_on=day,
        )
    )
    sim.next_tick()

    page = sim.get_fund(ana, fund_id)
    assert sim._engine.broker.get_positions(caio.client_id)[TICKER].size == 10
    assert (page.offer_sold, page.offer_raised) == (5, 500)
    assert page.offer_buyers is not None
    assert [(b.user_id, b.quotas) for b in page.offer_buyers] == [(bruno.id, 5)]


def resumed_page(sim: Simulation, viewer: UserDTO, fund_id: int):
    """Grava a partida como está, retoma e devolve a página da gestora na partida retomada."""
    summary = repository.simulation.get_simulation(sim.settings.id)
    assert summary is not None
    SimulationLoader.load(summary)
    return SimulationManager.get_active_simulation().get_fund(viewer, fund_id)


def test_resumed_match_keeps_the_offer_in_progress(started):  # noqa: F811
    sim, _ana, bruno, fund_id = offered_match()
    before = sim.get_fund(bruno, fund_id)

    after = resumed_page(sim, bruno, fund_id)

    assert (after.offer_quotas, after.offer_price) == (20, 100)
    assert (after.offer_sold, after.offer_raised) == (5, 500)
    assert after.offer_buyers == before.offer_buyers
    assert after.offer_closed_on is None


def test_resumed_match_keeps_the_closed_offer(started):  # noqa: F811
    sim, ana, _bruno, fund_id = offered_match()
    sim.close_fund_offer(ana, fund_id)
    before = sim.get_fund(ana, fund_id)

    after = resumed_page(sim, ana, fund_id)

    assert after.offer_closed_on == before.offer_closed_on is not None
    closed = next(m for m in after.movements if m.type == "offer_closed")
    opened = next(m for m in after.movements if m.type == "offer_opened")
    assert (opened.quotas, closed.quotas, closed.amount) == (20, 5, 500)


def test_viewer_sees_his_own_quotas_value_and_return(started):  # noqa: F811
    sim, ana = empty_match("Bruno", "Caio")
    bruno = player(sim, "Bruno")
    caio = player(sim, "Caio")
    fund_id = fund_with_cash(sim, ana)
    sim.open_fund_offer(ana, fund_id, 20)
    buy_at_market(sim, bruno, TICKER, 5)

    mine = sim.get_fund(bruno, fund_id)
    manager = sim.get_fund(ana, fund_id)
    without_quotas = sim.get_fund(caio, fund_id)

    assert (mine.my_quotas, mine.my_value, mine.my_return) == (5, 500, 0)
    assert (manager.my_quotas, manager.my_value) == (50, 5000)
    assert (
        without_quotas.my_quotas,
        without_quotas.my_value,
        without_quotas.my_return,
    ) == (0, 0, None)


def test_a_month_in_shows_report_fees_series_and_returns(started):  # noqa: F811
    sim, ana, _bruno, fund_id = offered_match()
    stock = next(
        ticker
        for ticker, asset in sim._engine.stocks.items()
        if asset.asset_class == AssetClass.STOCK
    )
    buy_for_fund(sim, fund_id, stock, 10)
    run_days(sim, 45)

    page = sim.get_fund(ana, fund_id)

    # A taxa de administração cai na virada do mês e vai para o gestor
    fees = [m for m in page.movements if m.type == "management_fee"]
    assert len(fees) == 2
    assert page.fees.received_12m == sum(m.amount for m in fees if m.amount)
    # 1% ao ano / 12 sobre o PL por cota (~R$ 100) das 55 cotas fora do formador
    assert page.fees.management_monthly_estimate == Decimal("4.56")
    assert page.fees.next_performance_on == date(2004, 9, 1)
    assert page.fees.performance_estimate == 0
    # Os movimentos vêm do mais novo para o mais antigo
    days = [m.day for m in page.movements]
    assert days == sorted(days, reverse=True)
    reports = [m for m in page.movements if m.type == "report_published"]
    assert [m.day for m in reports] == [date(2004, 5, 3), date(2004, 4, 1)]
    # O relatório é o do último pregão antes da virada de maio, com a ação comprada
    assert page.last_report is not None
    assert page.last_report.day == date(2004, 4, 30)
    held = {p.ticker for p in page.last_report.positions}
    assert held == {None, stock}
    assert sum(p.fraction for p in page.last_report.positions) == 1
    # A série abre no dia da oferta, ao preço dela, e a gestora é mais nova que 12 meses
    assert page.series[0].day == date(2004, 3, 2)
    assert page.series[0].nav == page.offer_price
    assert page.series[-1].day == sim._current_date
    assert page.return_since == page.series[0].day
    assert page.nav is not None
    assert page.return_12m == page.nav / page.series[0].nav - 1
    assert page.cdi_12m is not None
    assert page.cdi_12m > 0


def test_report_is_kept_until_the_next_month_turn(started):  # noqa: F811
    sim, ana, bruno, fund_id = offered_match()
    run_days(sim, 45)
    first = sim.get_fund(ana, fund_id).last_report
    fund = book_of(sim).by_id(fund_id)

    again = sim.get_fund(bruno, fund_id).last_report

    assert first is not None
    assert again is first
    assert fund.report is not None
    assert fund.report[1] is first


def test_there_is_no_report_before_the_first_month_turn(started):  # noqa: F811
    sim, ana, _bruno, fund_id = offered_match()
    run_days(sim, 5)

    page = sim.get_fund(ana, fund_id)

    assert page.last_report is None
    assert page.return_since is not None


@pytest.fixture
def sent_events(monkeypatch) -> list[str]:
    """Os nomes dos eventos de tempo real que a partida emite, na ordem."""
    sent: list[str] = []
    monkeypatch.setattr(
        RealtimeBrokerManager,
        "get_broker",
        lambda: SimpleNamespace(
            notify=lambda event, payload, to=None: sent.append(event)
        ),
    )
    return sent


def test_the_close_of_the_session_announces_the_funds_update(flow, sent_events):
    sim, ana = flow
    fund_with_cash(sim, ana)
    sent_events.clear()

    sim.next_tick()

    assert sent_events.count("funds_update") == 1


def test_each_manager_action_announces_the_funds_update(flow, sent_events):
    sim, ana = flow

    fund = sim.found_fund(ana, found_request())
    assert sent_events.count("funds_update") == 1
    sim.contribute_to_fund(ana, fund.id, FundContributionRequest(cash=Decimal(5000)))
    assert sent_events.count("funds_update") == 2
    sim.open_fund_offer(ana, fund.id, 20)
    assert sent_events.count("funds_update") == 3
    sim.set_fund_fees(
        ana,
        fund.id,
        FundFeesRequest(
            management_fee=Decimal("0.02"), performance_fee=Decimal("0.20")
        ),
    )
    assert sent_events.count("funds_update") == 4
    sim.close_fund_offer(ana, fund.id)
    assert sent_events.count("funds_update") == 5


def test_a_quota_trade_announces_the_funds_update(started, sent_events):  # noqa: F811
    sim, ana = empty_match("Bruno")
    bruno = player(sim, "Bruno")
    fund_id = fund_with_cash(sim, ana)
    sim.open_fund_offer(ana, fund_id, 20)
    sent_events.clear()

    sim.create_order(
        MarketOrder(
            client_id=bruno.client_id,
            ticker=TICKER,
            size=Decimal(5),
            action=OrderAction.BUY,
            placed_on=sim._current_date,
        )
    )

    assert sent_events.count("funds_update") == 1


def test_the_managers_accounts_share_one_owner_in_the_order_book(started):  # noqa: F811
    sim, ana = empty_match("Bruno")
    bruno = player(sim, "Bruno")
    fund = book_of(sim).by_id(fund_with_cash(sim, ana))

    assert sim._account_owner(ana.client_id) == ana.id
    assert sim._account_owner(fund.account.client_id) == ana.id
    assert sim._account_owner(bruno.client_id) == bruno.id
    assert sim._account_owner(MARKET_CLIENT_ID) is None


def test_fund_does_not_trade_with_the_managers_personal_account(started):  # noqa: F811
    sim, ana = empty_match()
    fund = book_of(sim).by_id(fund_with_cash(sim, ana))
    engine = sim._engine.matching_engine
    sale = LimitOrder(
        client_id=ana.client_id,
        ticker=TICKER,
        price=100.0,
        size=Decimal(10),
        action=OrderAction.SELL,
        placed_on=sim._current_date,
    )
    engine.submit(sale)

    purchase = LimitOrder(
        client_id=fund.account.client_id,
        ticker=TICKER,
        price=101.0,
        size=Decimal(10),
        action=OrderAction.BUY,
        placed_on=sim._current_date,
    )
    engine.submit(purchase)

    assert purchase.status is OrderStatus.CANCELED
    assert sale.remaining == 10
    assert engine.order_book.find(sale.id) is sale
