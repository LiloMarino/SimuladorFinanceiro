from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

import pytest

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.fund import FundDayDTO, FundDTO
from backend.core.dto.stock import StockDTO
from backend.core.enum import AssetClass, OrderAction
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.funds import fund_book as fund_book_module
from backend.features.funds.fund_account import DayTrades
from backend.features.funds.fund_book import (
    FundBook,
    cdi_growth,
    close_candle,
    months_between,
    nav_per_quota,
)
from backend.features.funds.ranking_price import RANKING_WINDOW
from backend.features.simulation.simulation_engine import (
    BalanceSheet,
    SimulationEngine,
)
from backend.features.variable_income.broker import Broker
from backend.features.variable_income.entities.order import (
    FUND_ISSUER_CLIENT_ID,
    FUND_MAKER_CLIENT_ID,
    MarketOrder,
)
from backend.features.variable_income.matching_engine import MatchingEngine
from tests.fakes import FakeSimulationEngine, client

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
        self.fund_stocks: dict[str, StockDTO] = {}

    def balance_sheet(self, client_id: UUID) -> BalanceSheet:
        return BalanceSheet(
            Decimal(0), Decimal(0), self.cash[client_id], Decimal(0), {}
        )

    def add_fund_stock(self, stock: StockDTO) -> None:
        self.stocks[stock.ticker] = stock

    update_market_data = SimulationEngine.update_market_data


@dataclass
class MemoryFunds:
    """O repositório de gestoras em memória."""

    funds: dict[int, FundDTO] = field(default_factory=dict)
    days_saved: dict[int, list[FundDayDTO]] = field(default_factory=dict)
    candles: list[CandleDTO] = field(default_factory=list)

    def create(self, *, simulation_id: int, **fields) -> FundDTO:
        fund = FundDTO(
            id=len(self.funds) + 1,
            portfolio_id=100 + len(self.funds),
            quotas=Decimal(0),
            maker_quotas=Decimal(0),
            maker_cash=Decimal(0),
            offer_remaining=None,
            listed_on=None,
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

    def save_candle(self, simulation_id: int, candle: CandleDTO) -> None:
        self.candles.append(candle)

    def last_close(
        self, simulation_id: int, stock_id: int, until: date
    ) -> float | None:
        closes = [c.close for c in self.candles if c.price_date <= until]
        return closes[-1] if closes else None


class Stocks:
    def add_stock(self, ticker: str, name: str, asset_class: AssetClass) -> StockDTO:
        return StockDTO(id=1, ticker=ticker, name=name, asset_class=asset_class)


@pytest.fixture(autouse=True)
def isolated(
    captured_events: list[BaseEventDTO], monkeypatch: pytest.MonkeyPatch
) -> list[BaseEventDTO]:
    monkeypatch.setattr(repository.portfolio, "get_equity_events", lambda _: [])
    monkeypatch.setattr(repository, "stock", Stocks())
    monkeypatch.setattr(SimulationManager, "_fund_portfolios", {})
    monkeypatch.setattr(fund_book_module, "index_daily_rate", lambda *_: DAILY_CDI)
    return captured_events


@pytest.fixture
def memory(monkeypatch: pytest.MonkeyPatch) -> MemoryFunds:
    memory = MemoryFunds()
    monkeypatch.setattr(repository, "fund", memory)
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


def _setup(memory: MemoryFunds, *, quotas: int = 1000, cash: int = 100000) -> Setup:
    engine = FundEngine()
    book = FundBook(1, engine, lambda user_id: MANAGER)
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
        FUND_MAKER_CLIENT_ID,
        FUND_ISSUER_CLIENT_ID,
    }
    assert {o.to_dto().player_nickname for o in orders} == {
        "Formador de mercado",
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
