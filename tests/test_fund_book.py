from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.fund import (
    FundAssemblyDTO,
    FundAssemblyVoteDTO,
    FundBuybackDTO,
    FundComanagerDTO,
    FundComanagerEventDTO,
    FundDayDTO,
    FundDirectedIssuanceDTO,
    FundDistributionDTO,
    FundDTO,
    FundIssuanceDTO,
    FundIssuanceRightDTO,
    FundOfferSaleDTO,
)
from backend.core.dto.stock import StockDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    AssetClass,
    FundAssemblyStatus,
    FundDirectedIssuanceStatus,
    OrderAction,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.fund_reference import FundReference
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.funds import fund_book as fund_book_module
from backend.features.funds.fund_book import (
    FundBook,
    cdi_growth,
    months_between,
    nav_per_quota,
    offer_ends_on,
    offer_session,
)
from backend.features.funds.performance import PERFORMANCE_WINDOW
from backend.features.funds.ranking_price import RANKING_WINDOW
from backend.features.market_maker.account import DayTrades
from backend.features.market_maker.candle import close_candle
from backend.features.notifications.news import Headline
from backend.features.simulation.simulation_engine import (
    BalanceSheet,
    SimulationEngine,
)
from backend.features.variable_income.broker import Broker
from backend.features.variable_income.entities.order import (
    FUND_ISSUER_CLIENT_ID,
    MARKET_MAKER_CLIENT_ID,
    LimitOrder,
    MarketOrder,
)
from backend.features.variable_income.entities.position import Position
from backend.features.variable_income.matching_engine import MatchingEngine
from tests.fakes import USER_ID, FakeSimulationEngine, client

TICKER = "AURA11"
TODAY = date(2020, 1, 6)
MANAGER_USER = 7
MANAGER = client("gestor")
BUYER = client("comprador")
DAILY_CDI = Decimal("0.0004")


class FundEngine(FakeSimulationEngine):
    """O motor em memória com o que o `FundBook` lê: corretora, livro, balanço e catálogo."""

    def __init__(self) -> None:
        super().__init__(current_date=TODAY)
        self.broker = Broker(self, threading.RLock())
        self.matching_engine = MatchingEngine(self.broker)
        self.ranking_prices: dict[str, Decimal] = {}
        self.fund_references: dict[str, FundReference] = {}
        self.created_stocks: dict[str, StockDTO] = {}

    def balance_sheet(self, client_id: UUID) -> BalanceSheet:
        # A taxa a pagar é dívida da conta, como no motor real
        return BalanceSheet(
            Decimal(0),
            Decimal(0),
            self.cash[client_id],
            self.fund_fee_payable.get(client_id, Decimal(0)),
            {},
            Decimal(0),
        )

    def add_created_stock(self, stock: StockDTO) -> None:
        self.stocks[stock.ticker] = stock

    update_market_data = SimulationEngine.update_market_data


@dataclass
class MemoryFunds:
    """O repositório de gestoras em memória."""

    funds: dict[int, FundDTO] = field(default_factory=dict)
    days_saved: dict[int, list[FundDayDTO]] = field(default_factory=dict)
    candles: list[CandleDTO] = field(default_factory=list)
    trades: list[EquityEventDTO] = field(default_factory=list)
    portfolio_events: list[EquityEventDTO] = field(default_factory=list)
    offer_sales_saved: dict[int, list[FundOfferSaleDTO]] = field(default_factory=dict)
    issuances_saved: dict[int, list[FundIssuanceDTO]] = field(default_factory=dict)
    rights_saved: dict[int, list[FundIssuanceRightDTO]] = field(default_factory=dict)
    buybacks_saved: dict[int, list[FundBuybackDTO]] = field(default_factory=dict)
    assemblies_saved: dict[int, list[FundAssemblyDTO]] = field(default_factory=dict)
    assembly_votes_saved: dict[int, dict[int, FundAssemblyVoteDTO]] = field(
        default_factory=dict
    )
    distributions_saved: dict[int, list[FundDistributionDTO]] = field(
        default_factory=dict
    )
    next_id: int = 1

    @property
    def all_sales(self) -> list[FundOfferSaleDTO]:
        return [s for sales in self.offer_sales_saved.values() for s in sales]

    def claim_stock(self, ticker: str, name: str) -> StockDTO | None:
        return StockDTO(id=1, ticker=ticker, name=name, asset_class=AssetClass.FUND)

    def create(self, *, simulation_id: int, **fields) -> FundDTO:
        fund = FundDTO(
            id=len(self.funds) + 1,
            portfolio_id=100 + len(self.funds),
            quotas=Decimal(0),
            maker_quotas=Decimal(0),
            maker_cash=Decimal(0),
            offer_remaining=None,
            listed_on=None,
            offer_quotas=None,
            offer_price=None,
            offer_closed_on=None,
            pending_management_fee=None,
            pending_performance_fee=None,
            pending_from=None,
            high_water_mark=None,
            high_water_mark_on=None,
            last_performance_on=None,
            **fields,
        )
        self.funds[fund.id] = fund
        return fund

    def of_simulation(self, simulation_id: int) -> list[FundDTO]:
        return list(self.funds.values())

    def save(self, fund: FundDTO) -> None:
        self.funds[fund.id] = fund

    def save_day(self, fund_id: int, day: FundDayDTO) -> None:
        self.days_saved.setdefault(fund_id, []).append(day)

    def days(self, fund_id: int, before: date, limit: int) -> list[FundDayDTO]:
        return [d for d in self.days_saved.get(fund_id, []) if d.day < before][-limit:]

    def drop_days_from(self, fund_id: int, day: date) -> None:
        self.days_saved[fund_id] = [
            d for d in self.days_saved.get(fund_id, []) if d.day < day
        ]

    def save_distribution(
        self, fund_id: int, distribution: FundDistributionDTO
    ) -> None:
        rows = self.distributions_saved.setdefault(fund_id, [])
        rows[:] = [r for r in rows if r.data_com != distribution.data_com]
        rows.append(distribution)

    def distributions(self, fund_id: int, before: date) -> list[FundDistributionDTO]:
        rows = self.distributions_saved.get(fund_id, [])
        return sorted(
            (r for r in rows if r.data_com < before), key=lambda r: r.data_com
        )

    def drop_distributions_from(self, fund_id: int, day: date) -> None:
        self.distributions_saved[fund_id] = [
            r for r in self.distributions_saved.get(fund_id, []) if r.data_com < day
        ]

    def record_offer_sale(self, fund_id: int, sale: FundOfferSaleDTO) -> None:
        self.offer_sales_saved.setdefault(fund_id, []).append(sale)

    def offer_sales(self, fund_id: int) -> list[FundOfferSaleDTO]:
        return [
            s for s in self.offer_sales_saved.get(fund_id, []) if s.issuance_id is None
        ]

    def issuance_sales(self, issuance_id: int) -> list[FundOfferSaleDTO]:
        return [s for s in self.all_sales if s.issuance_id == issuance_id]

    def create_issuance(
        self,
        fund_id: int,
        issuance: FundIssuanceDTO,
        rights: list[FundIssuanceRightDTO],
    ) -> FundIssuanceDTO:
        created = issuance.model_copy(update={"id": self.next_id})
        self.next_id += 1
        self.issuances_saved.setdefault(fund_id, []).append(created)
        self.rights_saved[created.id] = list(rights)
        return created

    def save_issuance(
        self, issuance: FundIssuanceDTO, rights: list[FundIssuanceRightDTO]
    ) -> None:
        for rows in self.issuances_saved.values():
            for index, row in enumerate(rows):
                if row.id == issuance.id:
                    rows[index] = issuance
        self.rights_saved[issuance.id] = list(rights)

    def issuances(self, fund_id: int) -> list[FundIssuanceDTO]:
        return list(self.issuances_saved.get(fund_id, []))

    def issuance_rights(self, issuance_id: int) -> list[FundIssuanceRightDTO]:
        return list(self.rights_saved.get(issuance_id, []))

    def create_buyback(self, fund_id: int, buyback: FundBuybackDTO) -> FundBuybackDTO:
        created = buyback.model_copy(update={"id": self.next_id})
        self.next_id += 1
        self.buybacks_saved.setdefault(fund_id, []).append(created)
        return created

    def save_buyback(self, buyback: FundBuybackDTO) -> None:
        for rows in self.buybacks_saved.values():
            for index, row in enumerate(rows):
                if row.id == buyback.id:
                    rows[index] = buyback

    def buybacks(self, fund_id: int) -> list[FundBuybackDTO]:
        return list(self.buybacks_saved.get(fund_id, []))

    def cancel_open_buybacks(self, fund_id: int) -> None:
        rows = self.buybacks_saved.get(fund_id, [])
        for index, row in enumerate(rows):
            if row.state == "open":
                rows[index] = row.model_copy(update={"state": "canceled"})

    def create_assembly(
        self, fund_id: int, assembly: FundAssemblyDTO
    ) -> FundAssemblyDTO:
        created = assembly.model_copy(update={"id": self.next_id})
        self.next_id += 1
        self.assemblies_saved.setdefault(fund_id, []).append(created)
        return created

    def save_assembly(self, assembly: FundAssemblyDTO) -> None:
        for rows in self.assemblies_saved.values():
            for index, row in enumerate(rows):
                if row.id == assembly.id:
                    rows[index] = assembly

    def assemblies(self, fund_id: int) -> list[FundAssemblyDTO]:
        return list(self.assemblies_saved.get(fund_id, []))

    def save_assembly_vote(self, assembly_id: int, vote: FundAssemblyVoteDTO) -> None:
        self.assembly_votes_saved.setdefault(assembly_id, {})[vote.user_id] = vote

    def assembly_votes(self, assembly_id: int) -> list[FundAssemblyVoteDTO]:
        return list(self.assembly_votes_saved.get(assembly_id, {}).values())

    def last_removal(self, simulation_id: int, user_id: int) -> date | None:
        removed = [
            a.closed_on
            for rows in self.assemblies_saved.values()
            for a in rows
            if a.previous_manager_user_id == user_id
            and a.status is FundAssemblyStatus.REPLACED
            and a.closed_on is not None
        ]
        return max(removed, default=None)

    def drop_offer_sales_from(self, fund_id: int, day: date) -> None:
        self.offer_sales_saved[fund_id] = [
            sale for sale in self.offer_sales_saved.get(fund_id, []) if sale.day < day
        ]

    def save_candle(self, simulation_id: int, candle: CandleDTO) -> None:
        self.candles.append(candle)

    def last_close(
        self, simulation_id: int, stock_id: int, until: date
    ) -> float | None:
        closes = [c.close for c in self.candles if c.price_date <= until]
        return closes[-1] if closes else None

    def last_traded_close(
        self, simulation_id: int, stock_id: int, until: date
    ) -> float | None:
        closes = [
            c.close for c in self.candles if c.price_date <= until and c.volume > 0
        ]
        return closes[-1] if closes else None

    def quota_trades(self, simulation_id: int, stock_id: int) -> list[EquityEventDTO]:
        return self.trades

    def portfolio_equity_events(
        self, simulation_id: int, portfolio_id: int
    ) -> list[EquityEventDTO]:
        return self.portfolio_events


@pytest.fixture(autouse=True)
def isolated(
    captured_events: list[BaseEventDTO], monkeypatch: pytest.MonkeyPatch
) -> list[BaseEventDTO]:
    monkeypatch.setattr(repository.portfolio, "get_equity_events", lambda _: [])
    monkeypatch.setattr(SimulationManager, "_fund_portfolios", {})
    monkeypatch.setattr(fund_book_module, "index_daily_rate", lambda *_: DAILY_CDI)
    return captured_events


@dataclass
class MemoryComanagers:
    """Os co-gestores e as entradas e saídas das gestoras em memória."""

    rows: dict[int, dict[int, FundComanagerDTO]] = field(default_factory=dict)
    logged: dict[int, list[FundComanagerEventDTO]] = field(default_factory=dict)

    def of_fund(self, fund_id: int) -> list[FundComanagerDTO]:
        found = self.rows.get(fund_id, {}).values()
        return sorted(found, key=lambda row: (row.invited_on, row.user_id))

    def save(self, fund_id: int, comanager: FundComanagerDTO) -> None:
        self.rows.setdefault(fund_id, {})[comanager.user_id] = comanager

    def delete(self, fund_id: int, user_id: int) -> None:
        self.rows.get(fund_id, {}).pop(user_id, None)

    def record_event(self, fund_id: int, event: FundComanagerEventDTO) -> None:
        self.logged.setdefault(fund_id, []).append(event)

    def events(self, fund_id: int) -> list[FundComanagerEventDTO]:
        return list(self.logged.get(fund_id, []))


@dataclass
class MemoryDirectedIssuances:
    """As emissões dirigidas das gestoras em memória."""

    rows: dict[int, tuple[int, FundDirectedIssuanceDTO]] = field(default_factory=dict)

    def pending_of_fund(self, fund_id: int) -> FundDirectedIssuanceDTO | None:
        offers = [
            row
            for owner, row in self.rows.values()
            if owner == fund_id and row.status is FundDirectedIssuanceStatus.OFFERED
        ]
        return offers[-1] if offers else None

    def settled_of_fund(self, fund_id: int) -> list[FundDirectedIssuanceDTO]:
        return [
            row
            for owner, row in self.rows.values()
            if owner == fund_id and row.status is FundDirectedIssuanceStatus.ACCEPTED
        ]

    def create(
        self,
        fund_id: int,
        buyer_user_id: int,
        quotas: Decimal,
        offered_on: date,
        status: FundDirectedIssuanceStatus,
        price: Decimal | None = None,
        settled_on: date | None = None,
    ) -> FundDirectedIssuanceDTO:
        row = FundDirectedIssuanceDTO(
            id=len(self.rows) + 1,
            buyer_user_id=buyer_user_id,
            quotas=quotas,
            offered_on=offered_on,
            status=status,
            price=price,
            settled_on=settled_on,
        )
        self.rows[row.id] = (fund_id, row)
        return row

    def close(
        self,
        issuance_id: int,
        status: FundDirectedIssuanceStatus,
        price: Decimal | None = None,
        settled_on: date | None = None,
    ) -> None:
        owner, row = self.rows[issuance_id]
        self.rows[issuance_id] = (
            owner,
            row.model_copy(
                update={"status": status, "price": price, "settled_on": settled_on}
            ),
        )


@pytest.fixture
def memory(monkeypatch: pytest.MonkeyPatch) -> MemoryFunds:
    memory = MemoryFunds()
    monkeypatch.setattr(repository, "fund", memory)
    monkeypatch.setattr(repository, "fund_comanager", MemoryComanagers())
    monkeypatch.setattr(repository, "fund_directed_issuance", MemoryDirectedIssuances())
    return memory


@dataclass
class Setup:
    engine: FundEngine
    book: FundBook
    memory: MemoryFunds

    @property
    def fund_client(self) -> UUID:
        return self.book.get(TICKER).account.client_id

    def tick(self, day: date) -> None:
        """Um pregão na ordem do tick: abertura, negócios do dia (feitos pelo teste) e fechamento."""
        self.engine.current_date = day
        self.book.on_open(day)

    def buy(self, size: int) -> None:
        self.engine.cash[BUYER] += Decimal(100000)
        self.engine.matching_engine.submit(
            MarketOrder(
                client_id=BUYER,
                ticker=TICKER,
                size=Decimal(size),
                action=OrderAction.BUY,
                placed_on=self.engine.current_date,
            )
        )


def _setup(
    memory: MemoryFunds,
    *,
    quotas: int = 1000,
    cash: int = 100000,
    publish: Callable[[date, Headline], None] | None = None,
    frozen_until: Callable[[int], date | None] | None = None,
    participants: Callable[[], list[UserDTO]] | None = None,
) -> Setup:
    engine = FundEngine()
    book = FundBook(
        1, engine, lambda user_id: MANAGER, publish, frozen_until, participants
    )
    book.found(
        ticker=TICKER,
        name="Aura",
        founder_user_id=MANAGER_USER,
        manager_user_id=MANAGER_USER,
        management_fee=Decimal("0.02"),
        performance_fee=Decimal("0.20"),
    )
    fund = book.get(TICKER)
    fund.account.quotas = Decimal(quotas)
    engine.cash[fund.account.client_id] = Decimal(cash)
    return Setup(engine, book, memory)


def test_nav_per_quota_divides_net_assets_by_quotas():
    """PL por cota = (caixa + ações + renda fixa - dívida) / cotas; sem cota não há PL."""
    assert nav_per_quota(
        Decimal(1000), Decimal(500), Decimal(300), Decimal(200), Decimal(100)
    ) == Decimal(16)
    assert (
        nav_per_quota(Decimal(1000), Decimal(0), Decimal(0), Decimal(0), Decimal(0))
        is None
    )


def test_candle_uses_first_and_last_trade_with_high_low_and_volume():
    trades = DayTrades()
    for size, price in ((10, "100"), (5, "104"), (8, "98"), (2, "101")):
        trades.add(Decimal(size), Decimal(price))
    stock = StockDTO(id=1, ticker=TICKER, name="Aura", asset_class=AssetClass.FUND)

    candle = close_candle(stock, TODAY, trades, 99.0, Decimal(100))

    assert (candle.open, candle.high, candle.low, candle.close) == (100, 104, 98, 101)
    assert candle.volume == 25


def test_candle_without_trades_repeats_previous_close_with_zero_volume():
    stock = StockDTO(id=1, ticker=TICKER, name="Aura", asset_class=AssetClass.FUND)

    repeated = close_candle(stock, TODAY, DayTrades(), 103.5, Decimal(100))
    debut = close_candle(stock, TODAY, DayTrades(), None, Decimal(100))

    assert (repeated.open, repeated.close, repeated.volume) == (103.5, 103.5, 0)
    assert debut.close == 100.0


def test_months_between_counts_calendar_months():
    assert months_between(date(2020, 1, 31), date(2020, 7, 1)) == 6
    assert months_between(date(2020, 11, 5), date(2021, 2, 1)) == 3


def test_cdi_growth_compounds_the_business_days_after_the_start():
    """De sexta a sexta seguinte são 5 dias úteis depois do início."""
    growth = cdi_growth(date(2020, 1, 10), date(2020, 1, 17))

    assert growth == (1 + DAILY_CDI) ** 5


def test_open_offer_lists_the_fund_and_sets_the_maker_stake(memory: MemoryFunds):
    """A oferta lista a gestora, o formador subscreve 10% das cotas com dinheiro que entra no caixa e o PL não muda."""
    setup = _setup(memory)
    nav_before = Decimal(100000) / Decimal(1000)

    setup.book.open_offer(TICKER, Decimal(200))

    fund = setup.book.get(TICKER)
    assert fund.listed
    assert fund.account.maker_quotas == 120  # floor(10% x 1200)
    assert fund.account.quotas == 1120
    assert fund.account.maker_cash == -120 * nav_before
    assert setup.engine.cash[setup.fund_client] == Decimal(100000) + 120 * nav_before
    assert fund.nav == nav_before
    assert (
        setup.book._nav(fund) == nav_before
    )  # o PL recalculado com as cotas do formador
    assert fund.terms.high_water_mark == nav_before
    assert memory.funds[fund.terms.id].listed_on == TODAY
    orders = setup.engine.matching_engine.order_book.get_orders(TICKER)
    assert {o.client_id for o in orders} == {
        MARKET_MAKER_CLIENT_ID,
        FUND_ISSUER_CLIENT_ID,
    }
    assert {o.to_dto().player_nickname for o in orders} == {
        "Mercado",
        "Oferta pública",
    }


def test_open_offer_twice_is_rejected(memory: MemoryFunds):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))

    with pytest.raises(ValueError, match="abre uma vez"):
        setup.book.open_offer(TICKER, Decimal(200))


def test_close_writes_candle_day_and_ranking_price(memory: MemoryFunds):
    """O fechamento grava a vela, a linha do dia e põe a vela no mercado; o preço de ranking
    passa a valer na carteira."""
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    setup.tick(TODAY + timedelta(days=1))
    setup.buy(10)

    setup.book.on_close(setup.engine.current_date)

    fund = setup.book.get(TICKER)
    [candle] = memory.candles
    assert candle.volume == 10
    assert candle.price_date == setup.engine.current_date
    [day] = memory.days_saved[fund.terms.id]
    assert day.traded_quantity == 10
    assert day.ranking_price == setup.engine.ranking_prices[TICKER]
    market_candle = setup.engine.matching_engine.market_data.get_last(TICKER)
    assert market_candle is not None and market_candle.close == candle.close
    assert fund.account.day.quantity == 0


def test_close_without_trades_repeats_the_close_with_zero_volume(memory: MemoryFunds):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    setup.tick(TODAY + timedelta(days=1))
    setup.buy(10)
    setup.book.on_close(setup.engine.current_date)

    setup.tick(TODAY + timedelta(days=2))
    setup.book.on_close(setup.engine.current_date)

    first, second = memory.candles
    assert second.close == first.close
    assert second.volume == 0


def test_trades_between_open_and_close_are_counted_once(memory: MemoryFunds):
    """Cada negócio entra no dia uma vez; o pregão seguinte começa vazio."""
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    setup.tick(TODAY + timedelta(days=1))
    setup.buy(4)
    setup.buy(6)

    setup.book.on_close(setup.engine.current_date)

    assert memory.candles[0].volume == 10
    assert setup.book.get(TICKER).account.take_day().quantity == 0


def test_ranking_window_keeps_the_last_twenty_days(memory: MemoryFunds):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    day = TODAY
    for _ in range(RANKING_WINDOW + 5):
        day += timedelta(days=1)
        setup.tick(day)
        setup.book.on_close(day)

    assert len(setup.book.get(TICKER).days) == RANKING_WINDOW


def test_reload_rebuilds_the_fund_from_the_saved_rows(memory: MemoryFunds):
    """Uma partida retomada reconstrói conta, janela do ranking e último fechamento dos registros."""
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    setup.tick(TODAY + timedelta(days=1))
    setup.buy(10)
    setup.book.on_close(setup.engine.current_date)
    before = setup.book.get(TICKER)

    reloaded = FundBook(1, setup.engine, lambda user_id: MANAGER).get(TICKER)

    assert reloaded.account.quotas == before.account.quotas
    assert reloaded.account.maker_quotas == before.account.maker_quotas
    assert reloaded.last_close == before.last_close
    assert reloaded.days == before.days


def test_close_adds_the_nav_of_the_day_to_the_performance_window(
    memory: MemoryFunds,
):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    fund = setup.book.get(TICKER)
    day = TODAY
    for _ in range(PERFORMANCE_WINDOW + 5):
        day += timedelta(days=1)
        setup.tick(day)
        setup.book.on_close(day)

    assert len(fund.navs) == PERFORMANCE_WINDOW
    assert fund.navs[-1].day == day
    assert fund.navs[-1].nav == fund.nav


def test_reload_rebuilds_the_performance_window_from_the_saved_days(
    memory: MemoryFunds,
):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    day = TODAY
    for _ in range(PERFORMANCE_WINDOW + 5):
        day += timedelta(days=1)
        setup.tick(day)
        setup.book.on_close(day)
    before = setup.book.get(TICKER).navs

    reloaded = FundBook(1, setup.engine, lambda user_id: MANAGER).get(TICKER)

    assert len(reloaded.navs) == PERFORMANCE_WINDOW
    assert reloaded.navs == before
    # A janela do ranking continua curta, mesmo com a de desempenho longa
    assert len(reloaded.days) == RANKING_WINDOW


def test_open_publishes_the_reference_with_the_fixed_price_of_the_offer(
    memory: MemoryFunds,
):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    listed_on = setup.book.get(TICKER).terms.listed_on
    assert listed_on is not None

    setup.tick(listed_on)
    first = setup.engine.fund_references[TICKER]
    last_day = offer_ends_on(listed_on)
    setup.tick(last_day)
    last = setup.engine.fund_references[TICKER]

    assert first.nav == 100.0
    assert first.fixed_price == 100.0
    assert not first.fixed_price_last_session
    assert last.fixed_price_last_session


def test_reference_has_no_fixed_price_after_the_offer_ends(memory: MemoryFunds):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    fund = setup.book.get(TICKER)
    assert fund.terms.listed_on is not None
    fund.account.offer_remaining = None

    setup.tick(offer_ends_on(fund.terms.listed_on) + timedelta(days=1))

    assert setup.engine.fund_references[TICKER].fixed_price is None


def test_fund_portfolio_is_registered_for_the_engine(memory: MemoryFunds):
    setup = _setup(memory)

    assert SimulationManager.find_fund_portfolio(setup.fund_client) is not None


def test_management_fee_moves_cash_from_the_fund_to_the_manager(memory: MemoryFunds):
    """A taxa mensal é taxa anual / 12 x PL x cotas fora do formador, do caixa da gestora
    para o do gestor."""
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    fund = setup.book.get(TICKER)
    nav = fund.nav
    assert nav is not None
    expected = (Decimal("0.02") / 12 * nav * fund.account.outside_quotas).quantize(
        Decimal("0.01"), "ROUND_DOWN"
    )
    fund_cash = setup.engine.cash[setup.fund_client]

    setup.book.on_month(date(2020, 2, 3))

    assert setup.engine.cash[MANAGER] == expected
    assert setup.engine.cash[setup.fund_client] == fund_cash - expected


def test_performance_waits_six_months_from_the_offer(memory: MemoryFunds):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    setup.engine.cash[setup.fund_client] *= 2
    setup.tick(date(2020, 6, 1))
    before = setup.book.get(TICKER).terms.last_performance_on

    setup.book.on_month(date(2020, 6, 1))

    assert setup.book.get(TICKER).terms.last_performance_on == before


def test_performance_charges_only_what_beat_the_cdi(memory: MemoryFunds):
    """No sexto mês a taxa incide sobre o PL acima da marca d'água corrigida pelo CDI, e a
    marca d'água passa a ser o PL depois da taxa."""
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    fund = setup.book.get(TICKER)
    mark = fund.terms.high_water_mark
    assert mark is not None
    setup.engine.cash[setup.fund_client] *= 2
    setup.tick(date(2020, 7, 1))
    nav = fund.nav
    assert nav is not None
    line = mark * cdi_growth(TODAY, date(2020, 7, 1))
    expected = (Decimal("0.20") * (nav - line) * fund.account.outside_quotas).quantize(
        Decimal("0.01"), "ROUND_DOWN"
    )
    management = (Decimal("0.02") / 12 * nav * fund.account.outside_quotas).quantize(
        Decimal("0.01"), "ROUND_DOWN"
    )

    setup.book.on_month(date(2020, 7, 1))

    assert setup.engine.cash[MANAGER] == management + expected
    assert fund.terms.last_performance_on == date(2020, 7, 1)
    assert fund.terms.high_water_mark_on == date(2020, 7, 1)
    assert fund.terms.high_water_mark is not None
    assert fund.terms.high_water_mark < nav


def test_performance_is_zero_below_the_cdi_line(memory: MemoryFunds):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    fund = setup.book.get(TICKER)
    mark = fund.terms.high_water_mark
    setup.tick(date(2020, 7, 1))
    management = (
        Decimal("0.02") / 12 * (fund.nav or Decimal(0)) * fund.account.outside_quotas
    ).quantize(Decimal("0.01"), "ROUND_DOWN")

    setup.book.on_month(date(2020, 7, 1))

    assert setup.engine.cash[MANAGER] == management
    assert fund.terms.high_water_mark == mark


def test_pending_fees_apply_when_their_month_arrives(memory: MemoryFunds):
    setup = _setup(memory)
    fund = setup.book.get(TICKER)
    fund.terms = fund.terms.model_copy(
        update={
            "pending_management_fee": Decimal("0.01"),
            "pending_performance_fee": Decimal("0.10"),
            "pending_from": date(2020, 2, 3),
        }
    )

    setup.book.on_month(date(2020, 1, 31))
    assert fund.terms.management_fee == Decimal("0.02")

    setup.book.on_month(date(2020, 2, 3))
    assert fund.terms.management_fee == Decimal("0.01")
    assert fund.terms.performance_fee == Decimal("0.10")
    assert fund.terms.pending_from is None


def _owing_setup(memory: MemoryFunds) -> tuple[Setup, Decimal]:
    """Uma gestora listada com R$ 10 em caixa; devolve também a taxa de administração do mês."""
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    fund = setup.book.get(TICKER)
    assert fund.nav is not None
    fee = (Decimal("0.02") / 12 * fund.nav * fund.account.outside_quotas).quantize(
        Decimal("0.01"), "ROUND_DOWN"
    )
    setup.engine.cash[setup.fund_client] = Decimal(10)
    return setup, fee


def test_fee_beyond_the_cash_becomes_payable_and_the_cash_stays_non_negative(
    memory: MemoryFunds,
):
    """O caixa de R$ 10 paga o que alcança; o resto fica como taxa a pagar e o gestor recebe só o pago."""
    setup, fee = _owing_setup(memory)
    fund = setup.book.get(TICKER)

    setup.book.on_month(date(2020, 2, 3))

    assert setup.engine.cash[setup.fund_client] == 0
    assert setup.engine.cash[MANAGER] == 10
    assert fund.terms.management_fee_payable == fee - 10
    assert fund.terms.month_fees == fee


def test_payable_fee_discounts_the_nav(memory: MemoryFunds):
    """A taxa a pagar entra como dívida no PL por cota: ele cai pelo valor devido."""
    setup, fee = _owing_setup(memory)
    fund = setup.book.get(TICKER)
    setup.book.on_month(date(2020, 2, 3))

    nav = setup.book._nav(fund)

    assert nav == -(fee - 10) / fund.account.quotas


def test_next_cash_pays_the_payable_fee_to_the_manager_before_anything_else(
    memory: MemoryFunds,
):
    setup, fee = _owing_setup(memory)
    fund = setup.book.get(TICKER)
    setup.book.on_month(date(2020, 2, 3))

    setup.engine.cash[setup.fund_client] += Decimal(1000)
    setup.tick(date(2020, 2, 4))

    assert fund.terms.fee_payable == 0
    assert setup.engine.cash[MANAGER] == fee
    assert setup.engine.cash[setup.fund_client] == Decimal(1000) - (fee - 10)


def test_partial_cash_pays_part_of_the_payable_fee(memory: MemoryFunds):
    setup, fee = _owing_setup(memory)
    fund = setup.book.get(TICKER)
    setup.book.on_month(date(2020, 2, 3))

    setup.engine.cash[setup.fund_client] += Decimal(5)
    setup.tick(date(2020, 2, 4))

    assert fund.terms.management_fee_payable == fee - 15
    assert setup.engine.cash[setup.fund_client] == 0


def test_payable_fee_is_saved_and_reloaded(memory: MemoryFunds):
    setup, fee = _owing_setup(memory)
    setup.book.on_month(date(2020, 2, 3))

    assert memory.funds[1].management_fee_payable == fee - 10


def test_the_closing_day_records_the_payable_fee(memory: MemoryFunds):
    setup, fee = _owing_setup(memory)
    setup.book.on_month(date(2020, 2, 3))

    _close_day(setup, date(2020, 2, 3))

    assert memory.days_saved[1][-1].fee_payable == fee - 10


def test_first_contribution_issues_quotas_at_one_hundred_and_moves_the_cash(
    memory: MemoryFunds,
):
    setup = _setup(memory, quotas=0, cash=0)
    setup.engine.cash[MANAGER] = Decimal(1050)

    issued = setup.book.contribute(TICKER, MANAGER, Decimal(1050), {})

    assert issued == 10  # floor(1050 / 100)
    fund = setup.book.get(TICKER)
    assert fund.account.quotas == 10
    assert setup.engine.cash[MANAGER] == 0
    assert setup.engine.cash[setup.fund_client] == 1050
    assert memory.funds[fund.terms.id].quotas == 10
    position = setup.engine.broker.get_positions(MANAGER)[TICKER]
    assert position.size == 10
    # As cotas nascem com o custo contábil do que foi levado: R$ 1.050 em 10 cotas
    assert position.avg_price == Decimal(105)


def test_next_contribution_issues_quotas_at_the_current_nav(memory: MemoryFunds):
    setup = _setup(memory, quotas=10, cash=1000)  # PL de 100 por cota
    setup.engine.cash[MANAGER] = Decimal(550)

    issued = setup.book.contribute(TICKER, MANAGER, Decimal(550), {})

    assert issued == 5  # floor(550 / 100)
    assert setup.book.get(TICKER).account.quotas == 15


def test_contribution_after_the_offer_is_rejected(memory: MemoryFunds):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    setup.engine.cash[MANAGER] = Decimal(1000)

    with pytest.raises(ConflictError, match="antes da oferta"):
        setup.book.contribute(TICKER, MANAGER, Decimal(1000), {})


def test_contribution_without_enough_cash_moves_nothing(memory: MemoryFunds):
    setup = _setup(memory, quotas=0, cash=0)
    setup.engine.cash[MANAGER] = Decimal(50)

    with pytest.raises(UnprocessableEntityError, match="Caixa insuficiente"):
        setup.book.contribute(TICKER, MANAGER, Decimal(100), {})

    assert setup.engine.cash[MANAGER] == 50
    assert setup.book.get(TICKER).account.quotas == 0


def test_contribution_below_one_quota_is_rejected(memory: MemoryFunds):
    setup = _setup(memory, quotas=0, cash=0)
    setup.engine.cash[MANAGER] = Decimal(99)

    with pytest.raises(UnprocessableEntityError, match="uma cota"):
        setup.book.contribute(TICKER, MANAGER, Decimal(99), {})


def test_contribution_of_an_unknown_asset_is_rejected(memory: MemoryFunds):
    setup = _setup(memory, quotas=0, cash=0)

    with pytest.raises(UnprocessableEntityError, match="não pode ser integralizado"):
        setup.book.contribute(TICKER, MANAGER, Decimal(0), {"XXXX3": Decimal(1)})


def test_new_fees_wait_for_the_month_turn_and_announce_when_listed(
    memory: MemoryFunds,
):
    published: list[tuple[date, Headline]] = []
    setup = _setup(
        memory, publish=lambda day, headline: published.append((day, headline))
    )
    setup.book.open_offer(TICKER, Decimal(200))
    published.clear()

    setup.book.set_fees(TICKER, Decimal("0.01"), Decimal("0.20"))

    terms = setup.book.get(TICKER).terms
    assert terms.management_fee == Decimal("0.02")
    assert terms.pending_management_fee == Decimal("0.01")
    assert terms.pending_performance_fee == Decimal("0.20")
    assert terms.pending_from == date(2020, 2, 3)  # primeiro dia útil de fevereiro
    assert [h.text for _, h in published] == [
        "AURA11 muda a taxa de administração para 1% ao ano"
    ]


def test_asking_for_the_current_fees_cancels_the_pending_ones(memory: MemoryFunds):
    setup = _setup(memory)
    setup.book.set_fees(TICKER, Decimal("0.01"), Decimal("0.10"))

    setup.book.set_fees(TICKER, Decimal("0.02"), Decimal("0.20"))

    terms = setup.book.get(TICKER).terms
    assert terms.pending_management_fee is None
    assert terms.pending_from is None


def test_fees_before_the_offer_are_not_announced(memory: MemoryFunds):
    published: list[tuple[date, Headline]] = []
    setup = _setup(
        memory, publish=lambda day, headline: published.append((day, headline))
    )

    setup.book.set_fees(TICKER, Decimal("0.01"), Decimal("0.10"))

    assert published == []


def test_summary_carries_the_live_nav_and_the_ranking_price(memory: MemoryFunds):
    setup = _setup(memory)
    setup.book.on_open(TODAY)

    summary = setup.book.summary(setup.book.get(TICKER))

    assert summary.nav == 100
    assert summary.ranking_price == setup.engine.ranking_prices[TICKER]
    assert summary.ticker == TICKER


def test_summary_price_is_the_last_trade_and_empty_before_the_first(
    memory: MemoryFunds,
):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    setup.tick(TODAY + timedelta(days=1))
    fund = setup.book.get(TICKER)

    assert setup.book.summary(fund).price is None
    setup.buy(10)
    during_the_day = setup.book.summary(fund).price
    setup.book.on_close(setup.engine.current_date)
    setup.tick(TODAY + timedelta(days=2))
    next_day = setup.book.summary(fund).price

    assert during_the_day == Decimal(100)
    assert next_day == during_the_day


def test_reload_recovers_the_last_trade_price_from_the_traded_candles(
    memory: MemoryFunds,
):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    setup.tick(TODAY + timedelta(days=1))
    setup.buy(10)
    setup.book.on_close(setup.engine.current_date)
    setup.tick(TODAY + timedelta(days=2))
    setup.book.on_close(setup.engine.current_date)
    assert memory.candles[-1].volume == 0

    reloaded = FundBook(1, setup.engine, lambda user_id: MANAGER).get(TICKER)

    assert reloaded.last_trade_price == Decimal(100)


def test_summary_names_the_manager_from_the_participants(memory: MemoryFunds):
    manager = UserDTO(id=MANAGER_USER, client_id=MANAGER, nickname="Ana")
    other = UserDTO(id=MANAGER_USER + 1, client_id=uuid4(), nickname="Bruno")
    setup = _setup(memory, participants=lambda: [other, manager])

    summary = setup.book.summary(setup.book.get(TICKER))

    assert summary.manager_nickname == "Ana"


def test_a_new_fund_counts_the_manager_since_from_the_founding_day(
    memory: MemoryFunds,
):
    setup = _setup(memory)

    assert setup.book.get(TICKER).terms.manager_since == TODAY


def test_unknown_fund_id_is_not_found(memory: MemoryFunds):
    setup = _setup(memory)

    with pytest.raises(NotFoundError):
        setup.book.by_id(999)


def test_found_rejects_a_ticker_whose_letters_belong_to_an_asset(
    memory: MemoryFunds, monkeypatch: pytest.MonkeyPatch
):
    setup = _setup(memory)
    monkeypatch.setattr(memory, "claim_stock", lambda *_: None)

    with pytest.raises(
        ConflictError, match="quatro letras deste ticker já são de um ativo"
    ):
        setup.book.found(
            ticker="ZETA11",
            name="Zeta",
            founder_user_id=8,
            manager_user_id=8,
            management_fee=Decimal("0.01"),
            performance_fee=Decimal("0.10"),
        )


def test_offer_lasts_five_business_days_counting_the_opening_day():
    """Aberta numa segunda, a oferta tem o pregão 1 na segunda e o 5 na sexta; fim de semana não conta."""
    monday = date(2020, 1, 6)

    assert offer_ends_on(monday) == date(2020, 1, 10)
    assert offer_ends_on(date(2020, 1, 9)) == date(2020, 1, 15)
    assert [offer_session(monday, date(2020, 1, d)) for d in (6, 7, 8, 9, 10)] == [
        1,
        2,
        3,
        4,
        5,
    ]
    assert offer_session(monday, date(2020, 1, 13)) == 5


def test_summary_shows_the_offer_session_and_end_date(memory: MemoryFunds):
    setup = _setup(memory)
    fund = setup.book.get(TICKER)
    assert setup.book.summary(fund).offer_session is None
    setup.book.open_offer(TICKER, Decimal(200))
    opening = setup.book.summary(fund)
    setup.engine.current_date = date(2020, 1, 8)
    third = setup.book.summary(fund)

    assert (opening.offer_session, opening.offer_ends_on) == (1, date(2020, 1, 10))
    assert (third.offer_session, third.offer_ends_on) == (3, date(2020, 1, 10))


def test_offer_closes_by_itself_at_the_end_of_the_fifth_session(memory: MemoryFunds):
    """Nos pregões 1 a 4 a oferta segue aberta; ao fim do quinto fecha, só as cotas vendidas existem e a gravação acompanha."""
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    fund = setup.book.get(TICKER)
    setup.tick(date(2020, 1, 7))
    setup.buy(50)
    quotas_after_sale = fund.account.quotas + 0

    for day in (7, 8, 9):
        setup.tick(date(2020, 1, day))
        setup.book.on_close(date(2020, 1, day))
        assert fund.account.offer_remaining is not None
    setup.tick(date(2020, 1, 10))
    setup.book.on_close(date(2020, 1, 10))

    assert fund.account.offer_remaining is None
    assert memory.funds[fund.terms.id].offer_remaining is None
    assert fund.account.quotas >= quotas_after_sale
    summary = setup.book.summary(fund)
    assert (summary.offer_session, summary.offer_ends_on) == (None, None)
    orders = setup.engine.matching_engine.order_book.get_orders(TICKER)
    assert FUND_ISSUER_CLIENT_ID not in {o.client_id for o in orders}


def test_manual_close_still_ends_the_offer_before_the_fifth_session(
    memory: MemoryFunds,
):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))

    setup.book.close_offer(TICKER)

    assert setup.book.get(TICKER).account.offer_remaining is None


def test_summary_carries_the_frozen_until_of_the_manager_who_governs(
    memory: MemoryFunds,
):
    term_end = date(2020, 12, 31)
    governing = {"on": True}
    setup = _setup(
        memory,
        frozen_until=lambda user_id: (
            term_end if governing["on"] and user_id == MANAGER_USER else None
        ),
    )
    fund = setup.book.get(TICKER)

    assert setup.book.summary(fund).frozen_until == term_end
    governing["on"] = False
    assert setup.book.summary(fund).frozen_until is None


def test_frozen_fund_does_not_charge_fees_and_charges_again_once_free(
    memory: MemoryFunds,
):
    """Enquanto o gestor governa nenhuma taxa corre; no mês em que a gestora volta, a cobrança retoma."""
    governing = {"on": True}
    setup = _setup(
        memory,
        frozen_until=lambda user_id: date(2020, 12, 31) if governing["on"] else None,
    )
    setup.book.open_offer(TICKER, Decimal(200))
    setup.engine.cash[setup.fund_client] *= 2
    fund = setup.book.get(TICKER)
    base = fund.terms.last_performance_on

    setup.tick(date(2020, 7, 1))
    fund_cash = setup.engine.cash[setup.fund_client]
    setup.book.on_month(date(2020, 7, 1))

    assert setup.engine.cash[MANAGER] == 0
    assert setup.engine.cash[setup.fund_client] == fund_cash
    assert fund.terms.last_performance_on == base

    governing["on"] = False
    setup.book.on_month(date(2020, 8, 3))

    assert setup.engine.cash[MANAGER] > 0
    assert fund.terms.last_performance_on == date(2020, 8, 3)


def test_on_office_cancels_the_open_orders_of_the_managers_funds_only(
    memory: MemoryFunds,
):
    setup = _setup(memory)
    fund_client = setup.fund_client
    setup.book.open_offer(TICKER, Decimal(200))
    resting = LimitOrder(
        client_id=fund_client,
        ticker=TICKER,
        size=Decimal(5),
        action=OrderAction.BUY,
        placed_on=TODAY,
        price=1.0,
    )
    setup.engine.matching_engine.submit(resting)
    assert fund_client in {
        o.client_id for o in setup.engine.matching_engine.order_book.get_orders(TICKER)
    }

    setup.book.on_office(MANAGER_USER + 1)
    still_there = fund_client in {
        o.client_id for o in setup.engine.matching_engine.order_book.get_orders(TICKER)
    }
    setup.book.on_office(MANAGER_USER)

    orders = setup.engine.matching_engine.order_book.get_orders(TICKER)
    assert still_there
    assert fund_client not in {o.client_id for o in orders}
    # O formador e a oferta seguem no livro: a sala continua negociando a cota
    assert {MARKET_MAKER_CLIENT_ID, FUND_ISSUER_CLIENT_ID} <= {
        o.client_id for o in orders
    }


def test_sold_out_offer_is_closed_and_not_shown_as_open(memory: MemoryFunds):
    """Vendida a última cota, a oferta está encerrada: sem saldo gravado, sem pregão e sem data no resumo."""
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(20))
    fund = setup.book.get(TICKER)
    assert setup.book.summary(fund).offer_session == 1

    fund.account.issue(Decimal(20))

    assert fund.account.offer_remaining is None
    summary = setup.book.summary(fund)
    assert (summary.offer_session, summary.offer_ends_on) == (None, None)
    setup.book.on_close(TODAY)
    assert memory.funds[fund.terms.id].offer_remaining is None


def test_partly_sold_offer_stays_open(memory: MemoryFunds):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(20))
    fund = setup.book.get(TICKER)

    fund.account.issue(Decimal(5))

    assert fund.account.offer_remaining == 15
    assert setup.book.summary(fund).offer_session == 1


def test_open_offer_stores_the_size_and_the_price_of_the_offer(memory: MemoryFunds):
    setup = _setup(memory)

    setup.book.open_offer(TICKER, Decimal(200))

    stored = memory.funds[setup.book.get(TICKER).terms.id]
    assert (stored.offer_quotas, stored.offer_price) == (Decimal(200), Decimal(100))
    assert stored.offer_closed_on is None


def test_a_purchase_from_the_offer_is_stored_as_a_sale_of_that_buyer(
    memory: MemoryFunds,
):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    fund = setup.book.get(TICKER)

    setup.buy(30)

    sales = memory.offer_sales(fund.terms.id)
    assert [(s.day, s.buyer_user_id, s.quotas, s.price) for s in sales] == [
        (TODAY, USER_ID, Decimal(30), Decimal(100))
    ]
    assert fund.terms.offer_closed_on is None


def test_the_sale_that_empties_the_offer_closes_it_on_that_day(memory: MemoryFunds):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(20))
    fund = setup.book.get(TICKER)

    setup.buy(20)

    assert fund.account.offer_remaining is None
    assert memory.funds[fund.terms.id].offer_closed_on == TODAY
    assert sum(s.quotas for s in memory.offer_sales(fund.terms.id)) == 20


def test_the_offer_that_ran_its_course_stores_the_last_session_as_closing_day(
    memory: MemoryFunds,
):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    fund = setup.book.get(TICKER)

    for day in (7, 8, 9):
        setup.tick(date(2020, 1, day))
        setup.book.on_close(date(2020, 1, day))
        assert memory.funds[fund.terms.id].offer_closed_on is None
    setup.tick(date(2020, 1, 10))
    setup.book.on_close(date(2020, 1, 10))

    assert memory.funds[fund.terms.id].offer_closed_on == date(2020, 1, 10)


def test_manual_close_stores_the_day_it_happened(memory: MemoryFunds):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))

    setup.book.close_offer(TICKER)

    terms = memory.funds[setup.book.get(TICKER).terms.id]
    assert terms.offer_closed_on == TODAY


def test_the_maker_bids_stay_below_the_offer_so_it_never_buys_from_it(
    memory: MemoryFunds,
):
    setup = _setup(memory)
    setup.book.open_offer(TICKER, Decimal(200))
    fund = setup.book.get(TICKER)
    for day in (7, 8):
        setup.tick(date(2020, 1, day))

    book = setup.engine.matching_engine.order_book
    best_bid, issuer = book.best_buy(TICKER), book.best_sell(TICKER)
    assert best_bid is not None and issuer is not None
    assert (best_bid.client_id, issuer.client_id) == (
        MARKET_MAKER_CLIENT_ID,
        FUND_ISSUER_CLIENT_ID,
    )
    assert best_bid.price < issuer.price
    assert memory.offer_sales(fund.terms.id) == []


# =========================
# Rendimentos mensais
# =========================

DATA_COM = date(2020, 1, 31)  # último pregão de janeiro
PAY_DAY = date(2020, 2, 3)  # primeiro pregão depois dele


def _holding_setup(memory: MemoryFunds) -> Setup:
    """Uma gestora listada em que o gestor tem as 1.000 cotas de origem e o comprador, 30 da oferta."""
    manager = UserDTO(id=MANAGER_USER, client_id=MANAGER, nickname="Ana")
    buyer = UserDTO(id=USER_ID, client_id=BUYER, nickname="Bia")
    setup = _setup(memory, participants=lambda: [manager, buyer])
    setup.book.open_offer(TICKER, Decimal(200))
    setup.engine.broker.get_positions(MANAGER)[TICKER] = Position(TICKER, Decimal(1000))
    setup.buy(30)
    return setup


def _close_day(setup: Setup, day: date) -> None:
    setup.tick(day)
    setup.book.on_close(day)


def _earn(setup: Setup, amount: str, kind: str = "dividends") -> None:
    """O lucro realizado entra no caixa da gestora e no acumulado do mês."""
    value = Decimal(amount)
    setup.engine.cash[setup.fund_client] += value
    setup.engine.record_realized(setup.fund_client, kind, value)  # type: ignore[arg-type]


def test_data_com_settles_the_month_and_resets_the_accumulators(memory: MemoryFunds):
    """No último pregão do mês o lucro realizado vira rendimento por cota e o mês zera."""
    setup = _holding_setup(memory)
    fund = setup.book.get(TICKER)
    _earn(setup, "1000")
    _earn(setup, "500", "sales_gain")
    outside = fund.account.outside_quotas

    _close_day(setup, DATA_COM)

    row = fund.distributions[-1]
    assert row.data_com == DATA_COM
    assert row.realized_profit == Decimal(1500)
    assert row.per_quota == (Decimal("0.95") * 1500 / outside).quantize(
        Decimal("0.000001"), "ROUND_DOWN"
    )
    assert row.paid_on is None
    assert fund.terms.month_dividends == 0
    assert fund.terms.month_sales_gain == 0
    assert memory.distributions_saved[fund.terms.id] == [row]


def test_a_day_that_is_not_the_data_com_settles_nothing(memory: MemoryFunds):
    setup = _holding_setup(memory)
    _earn(setup, "1000")

    _close_day(setup, date(2020, 1, 30))

    fund = setup.book.get(TICKER)
    assert fund.distributions == []
    assert fund.terms.month_dividends == 1000


def test_yield_is_paid_at_the_next_open_as_a_dividend_of_the_quota(
    memory: MemoryFunds,
):
    """Cada cotista recebe quotas x rendimento por cota como provento da cota, e o caixa da
    gestora paga o total uma vez."""
    setup = _holding_setup(memory)
    fund = setup.book.get(TICKER)
    _earn(setup, "1000")
    _close_day(setup, DATA_COM)
    per_quota = fund.distributions[-1].per_quota
    cash = setup.engine.cash[setup.fund_client]

    setup.tick(PAY_DAY)

    manager_pay = (MANAGER, TICKER, Decimal(1000) * per_quota)
    buyer_pay = (
        BUYER,
        TICKER,
        (Decimal(30) * per_quota).quantize(Decimal("0.01"), "ROUND_DOWN"),
    )
    assert sorted(setup.engine.dividends, key=lambda d: d[2]) == sorted(
        [manager_pay, buyer_pay], key=lambda d: d[2]
    )
    paid = manager_pay[2] + buyer_pay[2]
    assert setup.engine.cash[setup.fund_client] == cash - paid
    row = fund.distributions[-1]
    assert (row.paid_on, row.paid_per_quota, row.paid) == (PAY_DAY, per_quota, paid)


def test_the_maker_receives_no_yield(memory: MemoryFunds):
    setup = _holding_setup(memory)
    _earn(setup, "1000")
    _close_day(setup, DATA_COM)

    setup.tick(PAY_DAY)

    receivers = {client for client, _, _ in setup.engine.dividends}
    assert receivers == {MANAGER, BUYER}


def test_short_cash_pays_cash_over_quotas_and_does_not_owe_the_rest(
    memory: MemoryFunds,
):
    """Com R$ 103 em caixa e 1.030 cotas, cada cota recebe R$ 0,10; o que faltou não é devido."""
    setup = _holding_setup(memory)
    fund = setup.book.get(TICKER)
    _earn(setup, "1000")
    _close_day(setup, DATA_COM)
    setup.engine.cash[setup.fund_client] = Decimal(103)

    setup.tick(PAY_DAY)

    row = fund.distributions[-1]
    assert row.paid_per_quota == Decimal("0.1")
    assert row.paid == Decimal(103)
    assert setup.engine.cash[setup.fund_client] == 0
    setup.tick(date(2020, 2, 4))
    assert fund.distributions[-1].paid == Decimal(103)


def test_the_yield_pays_only_the_cash_left_after_the_payable_fee(memory: MemoryFunds):
    """Com R$ 600 em caixa e R$ 500 de taxa a pagar, a taxa sai primeiro e o rendimento paga os R$ 100 que sobram."""
    setup = _holding_setup(memory)
    fund = setup.book.get(TICKER)
    _earn(setup, "1000")
    _close_day(setup, DATA_COM)
    fund.terms = fund.terms.model_copy(update={"performance_fee_payable": Decimal(500)})
    setup.engine.cash[setup.fund_client] = Decimal(600)

    setup.tick(PAY_DAY)

    row = fund.distributions[-1]
    assert fund.terms.fee_payable == 0
    assert row.paid is not None
    assert 0 < row.paid <= 100
    assert setup.engine.cash[setup.fund_client] >= 0


def test_the_distribution_plan_counts_the_payable_fee_against_the_cash(
    memory: MemoryFunds,
):
    setup = _holding_setup(memory)
    fund = setup.book.get(TICKER)
    _earn(setup, "1000")
    setup.engine.cash[setup.fund_client] = Decimal(1000)
    assert setup.book.distribution_plan(fund).cash_enough

    fund.terms = fund.terms.model_copy(update={"management_fee_payable": Decimal(500)})

    assert not setup.book.distribution_plan(fund).cash_enough


def test_a_losing_month_distributes_nothing(memory: MemoryFunds):
    """Taxas pagas maiores que o ganho dão lucro negativo: nada é pago e o prejuízo não passa
    para o mês seguinte."""
    setup = _holding_setup(memory)
    fund = setup.book.get(TICKER)
    fund.terms = fund.terms.model_copy(update={"month_fees": Decimal(100)})

    _close_day(setup, DATA_COM)
    setup.tick(PAY_DAY)

    row = fund.distributions[-1]
    assert (row.realized_profit, row.per_quota, row.paid) == (
        Decimal(-100),
        Decimal(0),
        Decimal(0),
    )
    assert setup.engine.dividends == []
    assert fund.terms.month_fees == 0


def test_month_fees_reduce_the_realized_profit(memory: MemoryFunds):
    setup = _holding_setup(memory)
    fund = setup.book.get(TICKER)
    _earn(setup, "1000")
    _close_day(setup, date(2020, 1, 30))
    setup.book.on_month(date(2020, 1, 30))
    fees = fund.terms.month_fees
    assert fees > 0

    _close_day(setup, DATA_COM)

    assert fund.distributions[-1].realized_profit == Decimal(1000) - fees


def test_new_distribution_rate_waits_for_the_month_turn(memory: MemoryFunds):
    setup = _holding_setup(memory)
    fund = setup.book.get(TICKER)
    assert fund.terms.distribution_rate == Decimal("0.95")

    setup.book.set_distribution(TICKER, Decimal("0.5"))

    assert fund.terms.distribution_rate == Decimal("0.95")
    assert fund.terms.pending_distribution_rate == Decimal("0.5")
    assert fund.terms.pending_from == PAY_DAY
    setup.book.on_month(DATA_COM)
    assert fund.terms.distribution_rate == Decimal("0.95")
    setup.book.on_month(PAY_DAY)
    assert fund.terms.distribution_rate == Decimal("0.5")
    assert fund.terms.pending_distribution_rate is None
    assert fund.terms.pending_from is None


def test_asking_for_the_current_rate_cancels_the_pending_one(memory: MemoryFunds):
    setup = _holding_setup(memory)
    setup.book.set_distribution(TICKER, Decimal("0.5"))

    setup.book.set_distribution(TICKER, Decimal("0.95"))

    terms = setup.book.get(TICKER).terms
    assert terms.pending_distribution_rate is None
    assert terms.pending_from is None


def test_rate_and_fees_share_the_effective_date(memory: MemoryFunds):
    """Pedir a taxa num lado não solta a data do que está pendente do outro."""
    setup = _holding_setup(memory)
    setup.book.set_distribution(TICKER, Decimal("0.5"))

    setup.book.set_fees(TICKER, Decimal("0.02"), Decimal("0.20"))
    terms = setup.book.get(TICKER).terms
    assert terms.pending_distribution_rate == Decimal("0.5")
    assert terms.pending_from == PAY_DAY

    setup.book.set_fees(TICKER, Decimal("0.01"), Decimal("0.20"))
    setup.book.set_distribution(TICKER, Decimal("0.95"))
    terms = setup.book.get(TICKER).terms
    assert terms.pending_distribution_rate is None
    assert terms.pending_management_fee == Decimal("0.01")
    assert terms.pending_from == PAY_DAY


def _performance_fee_after_yield(memory: MemoryFunds, rate: str) -> Decimal:
    """A taxa de performance do semestre numa gestora que rende `rate` do lucro de R$ 20.000
    do mês e retém o resto."""
    setup = _holding_setup(memory)
    fund = setup.book.get(TICKER)
    fund.terms = fund.terms.model_copy(update={"distribution_rate": Decimal(rate)})
    _earn(setup, "20000")
    # Sem a taxa de administração, a diferença entre as gestoras é só o rendimento
    fund.terms = fund.terms.model_copy(update={"management_fee": Decimal(0)})
    _close_day(setup, DATA_COM)
    setup.tick(PAY_DAY)
    setup.tick(date(2020, 7, 1))
    manager_cash = setup.engine.cash[MANAGER]
    setup.book.on_month(date(2020, 7, 1))
    return setup.engine.cash[MANAGER] - manager_cash


def test_yield_does_not_change_the_performance_fee(
    memory: MemoryFunds, monkeypatch: pytest.MonkeyPatch
):
    """Duas gestoras com o mesmo retorno total, uma rendendo 95% do lucro e a outra 0%, pagam
    a mesma taxa de performance."""
    distributing = _performance_fee_after_yield(memory, "0.95")
    monkeypatch.setattr(SimulationManager, "_fund_portfolios", {})
    other = MemoryFunds()
    monkeypatch.setattr(repository, "fund", other)
    retaining = _performance_fee_after_yield(other, "0")

    assert retaining > 0
    assert distributing == pytest.approx(retaining, abs=Decimal("0.05"))


def test_reload_keeps_the_settled_rows_and_drops_the_later_ones(memory: MemoryFunds):
    setup = _holding_setup(memory)
    fund = setup.book.get(TICKER)
    _earn(setup, "1000")
    _close_day(setup, DATA_COM)
    setup.tick(PAY_DAY)
    # Uma apuração gravada depois do dia retomado é refeita pelo tick
    memory.save_distribution(
        fund.terms.id,
        fund.distributions[-1].model_copy(update={"data_com": date(2020, 2, 28)}),
    )
    setup.engine.current_date = PAY_DAY

    reloaded = FundBook(1, setup.engine, lambda user_id: MANAGER).get(TICKER)

    assert [d.data_com for d in reloaded.distributions] == [DATA_COM]
