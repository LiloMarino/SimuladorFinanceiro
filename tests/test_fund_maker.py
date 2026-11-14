from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.enum import OrderAction
from backend.core.exceptions import InsufficentPositionError
from backend.features.funds.fund_account import FundAccount
from backend.features.funds.fund_maker import (
    BAND,
    DEPTH,
    FundMaker,
)
from backend.features.funds.fund_offer import FundOffer
from backend.features.funds.ranking_price import TradedDay, ranking_price
from backend.features.variable_income.broker import Broker
from backend.features.variable_income.entities.order import (
    FUND_ISSUER_CLIENT_ID,
    FUND_MAKER_CLIENT_ID,
    LimitOrder,
    MarketOrder,
)
from backend.features.variable_income.entities.position import Position
from backend.features.variable_income.matching_engine import MatchingEngine
from tests.fakes import FakeSimulationEngine, client

TICKER = "AURA11"
TODAY = date(2020, 1, 6)
FUND = client("gestora")
BUYER = client("buyer")
SELLER = client("seller")
NAV = Decimal(100)


@dataclass(frozen=True)
class Fill:
    taker: object
    maker: object
    price: float
    quantity: Decimal

    @property
    def involves_maker(self) -> bool:
        return FUND_MAKER_CLIENT_ID in (self.taker, self.maker)


class RecordingBroker(Broker):
    """O broker real, que também anota cada negócio."""

    fills: list[Fill]

    def execute_trade(
        self,
        *,
        taker_order,
        maker_order,
        size: Decimal,
        price: float,
    ) -> None:
        super().execute_trade(
            taker_order=taker_order, maker_order=maker_order, size=size, price=price
        )
        self.fills.append(
            Fill(taker_order.client_id, maker_order.client_id, price, size)
        )


class Market:
    """O motor real, em memória, com o formador e a oferta de uma gestora."""

    def __init__(
        self, *, quotas: int, maker_quotas: int, cash: dict[str, str] | None = None
    ) -> None:
        self.simulation = FakeSimulationEngine(
            cash={client(name): Decimal(value) for name, value in (cash or {}).items()}
        )
        self.broker = RecordingBroker(self.simulation, threading.RLock())
        self.broker.fills = []
        self.matching = MatchingEngine(self.broker)
        self.account = FundAccount(
            client_id=FUND,
            quotas=Decimal(quotas),
            maker_quotas=Decimal(maker_quotas),
        )
        self.broker.fund_accounts[TICKER] = self.account
        self.maker = FundMaker(self.matching, self.broker.fund_accounts)
        self.offer = FundOffer(self.matching, self.broker.fund_accounts)

    @property
    def fills(self) -> list[Fill]:
        return self.broker.fills

    def refresh(self, nav: float = float(NAV)) -> None:
        self.maker.refresh(TICKER, nav, self.account.quotas, TODAY)

    def give(self, client_id, quantity: int, price: int = 100) -> None:
        """Cotas já na mão do jogador, como se ele as tivesse comprado antes."""
        self.broker._positions[client_id] = {
            TICKER: Position(
                TICKER,
                size=Decimal(quantity),
                total_cost=Decimal(quantity * price),
                avg_price=Decimal(price),
            )
        }

    def limit(self, client_id, action: OrderAction, price: float, size: int):
        return LimitOrder(
            client_id=client_id,
            ticker=TICKER,
            size=Decimal(size),
            action=action,
            placed_on=TODAY,
            price=price,
        )

    def market(self, client_id, action: OrderAction, size: int) -> MarketOrder:
        return MarketOrder(
            client_id=client_id,
            ticker=TICKER,
            size=Decimal(size),
            action=action,
            placed_on=TODAY,
        )

    def maker_orders(self, action: OrderAction) -> list[LimitOrder]:
        return [
            o
            for o in self.matching.order_book.get_orders(TICKER)
            if isinstance(o, LimitOrder)
            and o.client_id == FUND_MAKER_CLIENT_ID
            and o.action == action
        ]

    def traded(self, fills: list[Fill]) -> TradedDay:
        return TradedDay(
            quantity=sum((f.quantity for f in fills), Decimal(0)),
            value=sum((Decimal(str(f.price)) * f.quantity for f in fills), Decimal(0)),
        )


@pytest.fixture(autouse=True)
def isolated(
    captured_events: list[BaseEventDTO], monkeypatch: pytest.MonkeyPatch
) -> list[BaseEventDTO]:
    monkeypatch.setattr(repository.portfolio, "get_equity_events", lambda _: [])
    return captured_events


def _ratio(fill: Fill) -> float:
    return fill.price / float(NAV)


def test_ladder_surrounds_nav_and_noise_trades_within_three_percent():
    """Sem procura, a escada fica em volta do PL e um ruído de compra e venda negocia a até
    ~3% do PL."""
    market = Market(quotas=1000, maker_quotas=100, cash={"buyer": "100000"})
    market.give(SELLER, 100)

    market.refresh()
    bids = market.maker_orders(OrderAction.BUY)
    asks = market.maker_orders(OrderAction.SELL)
    assert max(o.price for o in bids) < float(NAV) < min(o.price for o in asks)
    assert min(o.price for o in bids) >= float(NAV) * (1 - BAND)
    assert max(o.price for o in asks) <= float(NAV) * (1 + BAND)
    assert sum(o.size for o in bids) <= Decimal(1000) * Decimal(str(DEPTH))

    for day in range(30):
        nav = float(NAV) * 1.001**day
        market.refresh(nav)
        market.matching.submit(market.market(BUYER, OrderAction.BUY, 2))
        market.matching.submit(market.market(SELLER, OrderAction.SELL, 2))
        last = market.fills[-2:]
        assert all(abs(f.price / nav - 1) <= 0.03 for f in last)

    assert len(market.fills) == 60
    assert all(f.involves_maker for f in market.fills)


def test_continuous_buying_walks_up_inside_band_and_creates_premium():
    """Com compras contínuas acima do último preço, o formador vende cada vez mais longe do
    PL, sem passar de 1,2 x PL, e o preço de ranking fica acima do PL (ágio)."""
    market = Market(quotas=1000, maker_quotas=400, cash={"buyer": "100000000"})
    days: list[TradedDay] = []
    last_close = float(NAV)
    daily_max: list[float] = []

    for _ in range(30):
        market.refresh()
        start = len(market.fills)
        market.matching.cancel_all(BUYER)
        price = round(last_close * 1.03, 2)
        market.matching.submit(market.limit(BUYER, OrderAction.BUY, price, 10))
        today = market.fills[start:]
        days.append(market.traded(today))
        if today:
            last_close = today[-1].price
            daily_max.append(max(f.price for f in today))

    assert max(daily_max) <= float(NAV) * (1 + BAND) + 0.01
    assert daily_max[-1] > daily_max[0]
    # Ranking no 20º pregão, com a janela cheia de negócios
    assert ranking_price(days[:20], NAV) > NAV
    sold = sum((f.quantity for f in market.fills), Decimal(0))
    assert market.account.maker_quotas == 400 - sold


def test_resting_buy_at_double_nav_is_filled_at_ladder_prices_inside_band():
    """Uma compra do jogador a 2 x PL deixada no livro é executada pelos níveis do formador,
    cada um ao seu preço, sem negócio do formador fora de [0,8 x PL; 1,2 x PL]."""
    market = Market(quotas=1000, maker_quotas=100, cash={"buyer": "1000000"})
    eager = market.limit(BUYER, OrderAction.BUY, 200, 100)
    market.matching.submit(eager)

    market.refresh()

    maker_fills = [f for f in market.fills if f.involves_maker]
    assert maker_fills
    assert sum(f.quantity for f in maker_fills) == eager.size - eager.remaining
    assert all(0.8 <= _ratio(f) <= 1.2 for f in maker_fills)
    assert all(f.price != 200 for f in market.fills)
    assert len({f.price for f in maker_fills}) > 1
    assert market.account.maker_quotas == 100 - sum(f.quantity for f in maker_fills)
    assert (
        market.simulation.cash[BUYER]
        == 1000000
        - sum(Decimal(str(f.price)) * f.quantity for f in maker_fills)
        - 200 * eager.remaining
    )


def test_resting_buy_above_first_level_pays_the_level_price():
    """PL de 95, compra do jogador parada a 101 e primeiro nível de venda a 96,90: o jogador
    compra a 96,90."""
    market = Market(quotas=1000, maker_quotas=100, cash={"buyer": "10000"})
    resting = market.limit(BUYER, OrderAction.BUY, 101, 3)
    market.matching.submit(resting)

    market.refresh(95)

    (fill,) = market.fills
    assert (fill.taker, fill.maker) == (FUND_MAKER_CLIENT_ID, BUYER)
    assert (fill.price, fill.quantity) == (96.9, 3)
    assert resting.remaining == 0
    assert market.simulation.cash[BUYER] == Decimal(10000) - Decimal("96.9") * 3
    assert market.broker.get_positions(BUYER)[TICKER].size == 3
    assert market.account.maker_quotas == 97


def test_resting_sell_below_first_level_is_bought_at_the_level_price():
    """A venda do jogador parada abaixo do primeiro nível de compra é comprada ao preço do
    nível, e o estoque do formador sobe."""
    market = Market(quotas=1000, maker_quotas=100)
    market.give(SELLER, 5)
    resting = market.limit(SELLER, OrderAction.SELL, 90, 2)
    market.matching.submit(resting)

    market.refresh()

    (fill,) = market.fills
    assert (fill.taker, fill.maker) == (FUND_MAKER_CLIENT_ID, SELLER)
    assert (fill.price, fill.quantity) == (98.0, 2)
    assert market.simulation.cash[SELLER] == 196
    assert market.account.maker_quotas == 102
    assert market.account.maker_cash == -196


def test_matching_sell_level_comes_out_of_the_stock():
    """A venda do formador que casa no refresh baixa o estoque, e a escada restante cabe no
    que sobrou dele."""
    market = Market(quotas=1000, maker_quotas=5, cash={"buyer": "100000"})
    market.matching.submit(market.limit(BUYER, OrderAction.BUY, 200, 4))

    market.refresh()

    assert sum(f.quantity for f in market.fills) == 4
    assert market.account.maker_quotas == 1
    assert sum(o.remaining for o in market.maker_orders(OrderAction.SELL)) <= 1


def test_refresh_replaces_the_previous_ladder():
    """O refresh tira a escada do dia anterior antes de pôr a nova."""
    market = Market(quotas=1000, maker_quotas=100)

    market.refresh(100)
    market.refresh(110)

    prices = [o.price for o in market.maker_orders(OrderAction.BUY)]
    assert prices and max(prices) < 110
    assert min(prices) >= 110 * (1 - BAND)
    assert len(prices) == len(set(prices))


def test_maker_without_stock_places_no_sell_orders():
    """Com o estoque zerado, o formador não põe ordem de venda."""
    market = Market(quotas=1000, maker_quotas=0)

    market.refresh()

    assert market.maker_orders(OrderAction.SELL) == []
    assert market.maker_orders(OrderAction.BUY)


def test_sell_ladder_is_capped_by_stock():
    """A venda é limitada pelo estoque, e a compra não tem limite."""
    market = Market(quotas=1000, maker_quotas=5)

    market.refresh()

    assert sum(o.size for o in market.maker_orders(OrderAction.SELL)) == 5
    assert sum(o.size for o in market.maker_orders(OrderAction.BUY)) > 5


def test_forced_trade_at_ten_times_nav_is_capped_in_ranking_price():
    """Um negócio forçado a 10 x PL entre dois jogadores leva o preço de ranking a no
    máximo 1,3 x PL."""
    market = Market(quotas=1000, maker_quotas=100, cash={"buyer": "100000000"})
    market.give(SELLER, 50)
    market.refresh()
    forced = float(NAV) * 10
    market.matching.submit(market.limit(SELLER, OrderAction.SELL, forced, 10))
    below = sum(
        o.remaining
        for o in market.matching.order_book.get_orders(TICKER)
        if o.action == OrderAction.SELL
        and isinstance(o, LimitOrder)
        and o.price < forced
    )
    market.matching.submit(
        market.limit(BUYER, OrderAction.BUY, forced, int(below) + 10)
    )

    day = market.traded(market.fills)
    raw_vwap = day.value / day.quantity
    assert any(f.price == forced and not f.involves_maker for f in market.fills)
    assert raw_vwap > NAV * Decimal("1.3")
    assert ranking_price([day], NAV) == NAV * Decimal("1.3")


def test_ranking_price_is_nav_without_trades_and_window_is_twenty_days():
    """Sem negócio nos 20 pregões, o preço de ranking vale o PL; só os 20 últimos contam."""
    assert ranking_price([], NAV) == NAV
    assert ranking_price([TradedDay(Decimal(0), Decimal(0))] * 5, NAV) == NAV

    old = TradedDay(Decimal(10), Decimal(1200))
    recent = TradedDay(Decimal(10), Decimal(1100))
    window = [old, *[recent] * 20]
    assert ranking_price(window, NAV) == Decimal(110)


def test_ranking_price_is_capped_below_too():
    """A trava vale nos dois lados: abaixo do PL, o piso é 0,7 x PL."""
    day = TradedDay(Decimal(10), Decimal(100))
    assert ranking_price([day], NAV) == NAV * Decimal("0.7")


def test_maker_trade_moves_synthetic_stock_without_reserving_or_events(
    isolated: list[BaseEventDTO],
):
    """O formador não reserva caixa nem posição, e o negócio dele baixa o estoque e sobe o
    caixa sintético sem gerar evento de ação."""
    market = Market(quotas=1000, maker_quotas=100, cash={"buyer": "10000"})
    market.refresh()

    assert market.simulation.cash[FUND_MAKER_CLIENT_ID] == 0
    market.matching.submit(market.market(BUYER, OrderAction.BUY, 3))

    first = market.fills[0]
    assert first.maker == FUND_MAKER_CLIENT_ID
    assert market.account.maker_quotas == 97
    assert market.account.maker_cash == Decimal(str(first.price)) * 3
    assert market.account.quotas == 1000
    assert market.simulation.cash[FUND_MAKER_CLIENT_ID] == 0
    assert [e.portfolio_id for e in isolated if isinstance(e, EquityEventDTO)] == [1]


def test_maker_buy_raises_stock_and_spends_synthetic_cash():
    """A compra do formador sobe `maker_quotas` e gasta o caixa sintético."""
    market = Market(quotas=1000, maker_quotas=0)
    market.give(SELLER, 20)
    market.refresh()

    market.matching.submit(market.market(SELLER, OrderAction.SELL, 3))

    assert market.account.maker_quotas == 3
    assert market.account.maker_cash == -Decimal(str(market.fills[0].price)) * 3
    assert market.simulation.cash[SELLER] == Decimal(str(market.fills[0].price)) * 3


def test_maker_cannot_sell_more_than_its_stock():
    """O estoque do formador não fica negativo."""
    account = FundAccount(client_id=FUND, quotas=Decimal(100), maker_quotas=Decimal(2))

    with pytest.raises(InsufficentPositionError):
        account.maker_trade(OrderAction.SELL, Decimal(3), Decimal(100))


def test_offer_sale_issues_quotas_and_credits_the_fund_cash():
    """A venda da oferta emite as cotas vendidas e põe o dinheiro no caixa da gestora; o
    que não vendeu não é emitido."""
    market = Market(quotas=1000, maker_quotas=0, cash={"buyer": "100000"})
    market.account.offer_remaining = Decimal(100)

    market.offer.refresh(TICKER, float(NAV), TODAY)
    market.matching.submit(market.market(BUYER, OrderAction.BUY, 30))

    assert market.account.quotas == 1030
    assert market.account.offer_remaining == 70
    assert market.simulation.cash[FUND] == 3000
    assert market.simulation.cash[BUYER] == 97000
    assert market.broker.get_positions(BUYER)[TICKER].size == 30
    assert market.simulation.cash[FUND_ISSUER_CLIENT_ID] == 0


def test_offer_sells_at_fair_value_against_a_buy_at_double_nav():
    """A oferta executa ao valor justo contra uma compra parada a 2 x PL, e o que sobra
    repousa na ordem da oferta."""
    market = Market(quotas=1000, maker_quotas=0, cash={"buyer": "100000"})
    market.account.offer_remaining = Decimal(100)
    resting = market.limit(BUYER, OrderAction.BUY, 200, 50)
    market.matching.submit(resting)

    market.offer.refresh(TICKER, float(NAV), TODAY)

    (fill,) = market.fills
    assert (fill.taker, fill.maker) == (FUND_ISSUER_CLIENT_ID, BUYER)
    assert (fill.price, fill.quantity) == (100, 50)
    assert market.account.quotas == 1050
    assert market.account.offer_remaining == 50
    assert market.simulation.cash[FUND] == 5000
    assert market.simulation.cash[BUYER] == 100000 - 5000
    (order,) = [
        o
        for o in market.matching.order_book.get_orders(TICKER)
        if o.client_id == FUND_ISSUER_CLIENT_ID
    ]
    assert order.remaining == 50


def test_offer_is_repriced_daily_and_can_be_closed():
    """A ordem da oferta é refeita ao PL do dia com o saldo que falta, e encerrar a oferta
    tira a ordem do livro sem emitir o resto."""
    market = Market(quotas=1000, maker_quotas=0, cash={"buyer": "100000"})
    market.account.offer_remaining = Decimal(100)
    market.offer.refresh(TICKER, 100, TODAY)
    market.matching.submit(market.market(BUYER, OrderAction.BUY, 30))

    market.offer.refresh(TICKER, 105, TODAY)
    (order,) = [
        o
        for o in market.matching.order_book.get_orders(TICKER)
        if o.client_id == FUND_ISSUER_CLIENT_ID
    ]
    assert isinstance(order, LimitOrder)
    assert (order.price, order.remaining) == (105, 70)

    market.offer.close(TICKER)

    assert market.matching.order_book.get_orders(TICKER) == []
    assert market.account.offer_remaining is None
    assert market.account.quotas == 1030


def test_offer_without_remaining_places_no_order():
    """Sem saldo a vender, a oferta não põe ordem."""
    market = Market(quotas=1000, maker_quotas=0)

    market.offer.refresh(TICKER, 100, TODAY)

    assert market.matching.order_book.get_orders(TICKER) == []


def test_player_buy_pays_the_ladder_level_price_not_the_limit():
    """A compra limitada de um jogador contra a escada paga o preço do nível, não o limite."""
    market = Market(quotas=1000, maker_quotas=100, cash={"buyer": "10000"})
    market.refresh()

    market.matching.submit(market.limit(BUYER, OrderAction.BUY, 130, 1))

    assert market.fills[0].price == 102
    assert market.simulation.cash[BUYER] == 10000 - 102
