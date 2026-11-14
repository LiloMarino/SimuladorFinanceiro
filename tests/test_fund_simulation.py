"""As gestoras dentro do tick da partida: vela, fechamento, catálogo, ranking e retomada."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.enum import AssetClass, OrderAction
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.player_colors import PLAYER_COLORS
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.strategy.intents import buy, sell
from backend.features.variable_income.entities.order import LimitOrder, MarketOrder
from backend.features.variable_income.entities.position import Position
from tests.fakes import simulation_settings
from tests.test_simulation_loader import new_user, started  # noqa: F401

START = date(2004, 3, 1)
CASH = Decimal(10000)
TICKER = "AURA11"


def fund_match() -> tuple[Simulation, int]:
    """Partida com a expansão das gestoras, uma jogadora e a gestora dela com 1.000 cotas ao PL de R$ 100."""
    ana = new_user("Ana")
    UserManager.player_auth(ana.client_id)
    simulation_id = repository.simulation.create_simulation(
        simulation_settings().model_copy(
            update={
                "start_date": START,
                "end_date": date(2004, 12, 31),
                "starting_cash": CASH,
                "funds_enabled": True,
            }
        )
    )
    repository.simulation_player.save(simulation_id, {ana.id: PLAYER_COLORS[0]})
    repository.portfolio.open(simulation_id, [ana.id], START, CASH)
    summary = repository.simulation.get_simulation(simulation_id)
    assert summary is not None
    SimulationLoader.load(summary)
    sim = SimulationManager.get_active_simulation()
    assert sim._funds is not None
    fund = sim._funds.found(
        ticker=TICKER,
        name="Aura",
        founder_user_id=ana.id,
        manager_user_id=ana.id,
        management_fee=Decimal("0.02"),
        performance_fee=Decimal("0.20"),
    )
    fund.account.quotas = Decimal(1000)
    sim._engine.add_cash(fund.account.client_id, Decimal(100000))
    sim._funds.open_offer(TICKER, Decimal(200))
    assert fund.nav == Decimal(100)  # a subscrição do formador não muda o PL por cota
    EventManager.flush()
    return sim, ana.id


@pytest.fixture
def match(started) -> tuple[Simulation, int]:  # noqa: F811
    return fund_match()


def test_tick_closes_the_quota_candle_and_the_fund_day(match):
    sim, _ = match
    assert sim._funds is not None
    fund = sim._funds.get(TICKER)

    sim.next_tick()

    candle = sim._engine.matching_engine.market_data.get_last(TICKER)
    assert candle is not None and candle.volume == 0
    simulation_id = sim.settings.id
    [stored] = repository.fund.days(fund.terms.id, date(2100, 1, 1), 10)
    assert stored.day == sim._current_date
    assert (
        repository.fund.last_close(simulation_id, fund.terms.stock_id, stored.day)
        == candle.close
    )


def test_quota_is_in_the_engine_catalog_but_not_in_the_imported_prices(match):
    sim, _ = match

    sim.next_tick()

    assert sim._engine.stocks[TICKER].asset_class is AssetClass.FUND
    assert TICKER not in {stock.ticker for stock in sim.get_stocks()}


def test_player_buying_the_quota_pays_the_ranking_price_in_the_snapshot(match):
    """O jogador compra no livro e o snapshot avalia a cota pelo preço de ranking, que o
    tick de fechamento já deixou pronto."""
    sim, user_id = match
    ana = next(
        u
        for u in repository.simulation_player.participants(sim.settings.id)
        if u.id == user_id
    )
    sim.next_tick()
    sim._engine.matching_engine.submit(
        MarketOrder(
            client_id=ana.client_id,
            ticker=TICKER,
            size=Decimal(10),
            action=OrderAction.BUY,
            placed_on=sim._current_date,
        )
    )

    sim.next_tick()

    held = sim._engine.broker.get_positions(ana.client_id)[TICKER]
    assert held.size == 10
    assert sim._engine.get_current_price(held) == sim._engine.ranking_prices[TICKER]


def test_fund_portfolio_stays_out_of_the_snapshots(match):
    sim, user_id = match

    sim.next_tick()

    portfolios = repository.portfolio.ids(sim.settings.id)
    assert set(portfolios) == {user_id}


def test_resumed_match_rebuilds_the_fund_from_the_saved_rows(match, started):  # noqa: F811
    sim, _ = match
    assert sim._funds is not None
    sim.next_tick()
    sim.next_tick()
    before = sim._funds.get(TICKER)
    summary = repository.simulation.get_simulation(sim.settings.id)
    assert summary is not None

    SimulationLoader.load(summary)

    resumed = SimulationManager.get_active_simulation()
    assert resumed._funds is not None
    after = resumed._funds.get(TICKER)
    assert after.account.quotas == before.account.quotas
    assert after.account.maker_quotas == before.account.maker_quotas
    assert after.terms.listed_on == before.terms.listed_on
    # A retomada já processa o primeiro pregão seguinte, que soma mais um dia à janela
    assert after.days[: len(before.days)] == before.days
    assert len(after.days) == len(before.days) + 1


def test_bot_buy_is_cut_to_twenty_percent_of_the_quotas(match):
    """O teto do bot é 20% das cotas (1.120 em circulação: 224), descontadas a posição e as
    compras abertas dele."""
    sim, user_id = match
    ana = next(
        u
        for u in repository.simulation_player.participants(sim.settings.id)
        if u.id == user_id
    )
    runner = sim._strategies
    assert runner._quantity_allowed(ana, buy(TICKER, 500, "teste")) == 224

    sim._engine.broker.get_positions(ana.client_id)[TICKER] = Position(
        TICKER, size=Decimal(100)
    )
    assert runner._quantity_allowed(ana, buy(TICKER, 500, "teste")) == 124

    resting = LimitOrder(
        client_id=ana.client_id,
        ticker=TICKER,
        size=Decimal(24),
        action=OrderAction.BUY,
        placed_on=sim._current_date,
        price=1.0,
    )
    sim._engine.matching_engine.order_book.add(resting)
    assert runner._quantity_allowed(ana, buy(TICKER, 500, "teste")) == 100
    assert runner._quantity_allowed(ana, buy(TICKER, 30, "teste")) == 30


def test_bot_at_the_ceiling_is_refused_and_selling_is_untouched(match):
    sim, user_id = match
    ana = next(
        u
        for u in repository.simulation_player.participants(sim.settings.id)
        if u.id == user_id
    )
    runner = sim._strategies
    sim._engine.broker.get_positions(ana.client_id)[TICKER] = Position(
        TICKER, size=Decimal(224)
    )

    with pytest.raises(ConflictError):
        runner._quantity_allowed(ana, buy(TICKER, 1, "teste"))
    assert runner._quantity_allowed(ana, sell(TICKER, 50, "teste")) == 50
    assert runner._quantity_allowed(ana, buy("BANK_A", 5000, "teste")) == 5000
