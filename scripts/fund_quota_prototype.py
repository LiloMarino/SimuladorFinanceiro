"""
Protótipo de calibração da cota das gestoras no livro de ofertas.

Roda o MatchingEngine e o OrderBook de verdade, em memória, com um broker próprio, duas
gestoras de patrimônio sintético, o formador de mercado sintético em volta do patrimônio
por cota (PL) e jogadores e bots que compram e vendem cotas. Responde às perguntas:

    (1) sem procura, a cota negocia perto do PL?
    (2) com compra contínua, o preço sobe dentro da faixa e aparece ágio?
    (3) o formador negocia fora da faixa?
    (4) um negócio forçado leva o preço de ranking além de 30% do PL?
    (5) numa sala de 2 há contraparte?
    (6) quanto custa cada modelo do formador?
    (7) numa partida, a gestora do gestor bom fica com ágio e a do ruim com deságio?

O formador tem dois modelos: o de estoque próprio (subscreve 10% das cotas na oferta
pública com dinheiro sintético, compra com ele e só vende o que tem) e o de emissão e
resgate (vende cotas novas, cujo dinheiro entra na gestora, e compra resgatando cotas com o
caixa dela; a diferença entre o preço e o PL vira ganho dos cotistas). E duas execuções: a de hoje, em que a ordem
sintética cruza com o que já está no livro ao preço de quem estava lá, e a passiva, em que o
formador só põe o nível que não cruza.

    uv run python -m scripts.fund_quota_prototype               # 20 rodadas por caso
    uv run python -m scripts.fund_quota_prototype --runs 10     # rodada rápida
    uv run python -m scripts.fund_quota_prototype --out numeros.json
"""

import argparse
import io
import json
import math
import sys
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from decimal import Decimal
from enum import StrEnum
from pathlib import Path
from typing import Any

import numpy as np

import backend.features.variable_income.matching_engine as matching_engine_module
from backend.core.enum import OrderAction
from backend.core.exceptions import InsufficentCashError, InsufficentPositionError
from backend.core.exceptions.http_exceptions import ConflictError
from backend.features.variable_income.broker import Broker
from backend.features.variable_income.entities.order import (
    LimitOrder,
    MarketOrder,
    Order,
)
from backend.features.variable_income.matching_engine import MatchingEngine

TRADING_DAYS = 252
CDI = 0.12
START = date(2026, 1, 1)
MAKER_ID = uuid.uuid5(uuid.NAMESPACE_DNS, "__FUND_MAKER__")
CENT = 0.01


class MakerModel(StrEnum):
    STOCK = "estoque"
    ISSUANCE = "emissao"


class Execution(StrEnum):
    CURRENT = "atual"
    PASSIVE = "passiva"


class Shape(StrEnum):
    UNIFORM = "uniforme"
    EDGE = "borda"
    CENTER = "centro"


@dataclass(frozen=True)
class MakerParams:
    band: float = 0.20
    # Profundidade de cada lado, em fração das cotas em circulação
    depth: float = 0.02
    levels: int = 10
    shape: Shape = Shape.UNIFORM
    model: MakerModel = MakerModel.STOCK
    execution: Execution = Execution.PASSIVE
    # Estoque próprio: fração das cotas que o formador subscreve na oferta pública
    stock_share: float = 0.10


@dataclass(frozen=True)
class FundParams:
    ticker: str
    # Retorno anual acima do CDI e volatilidade anual da carteira de risco
    excess: float
    volatility: float
    quotas: int = 1000
    nav: float = 100.0
    cash_share: float = 0.2


GOOD = FundParams("AURA11", excess=0.08, volatility=0.20)
BAD = FundParams("BETA11", excess=-0.05, volatility=0.30)


def _silence_engine() -> None:
    """O motor avisa o front a cada ordem; aqui os avisos e os DTOs viram no-op."""

    class Silent:
        def __init__(self, **_: object) -> None:
            pass

        def to_json(self) -> None:
            return None

    matching_engine_module.notify = lambda **_: None
    for name in (
        "OrderEventDTO",
        "OrderBookSnapshotEventDTO",
        "OrderExecutedEventDTO",
        "OrderPartialExecutedEventDTO",
    ):
        setattr(matching_engine_module, name, Silent)
    setattr(Order, "to_dto", lambda _self: None)  # noqa: B010


# =========================
# Gestora
# =========================


@dataclass
class Fund:
    params: FundParams
    risky: float
    cash: float
    quotas: float
    nav_history: list[float] = field(default_factory=list)
    # Ganho dos cotistas com a emissão acima do PL e o resgate abaixo dele
    spread: float = 0.0

    @classmethod
    def found(cls, params: FundParams) -> "Fund":
        equity = params.quotas * params.nav
        return cls(
            params=params,
            risky=equity * (1 - params.cash_share),
            cash=equity * params.cash_share,
            quotas=params.quotas,
        )

    @property
    def equity(self) -> float:
        return self.risky + self.cash

    @property
    def nav(self) -> float:
        return self.equity / self.quotas

    def advance(self, rng: np.random.Generator) -> None:
        mu = CDI + self.params.excess
        sigma = self.params.volatility
        dt = 1 / TRADING_DAYS
        shock = rng.standard_normal()
        self.risky *= math.exp((mu - sigma**2 / 2) * dt + sigma * math.sqrt(dt) * shock)
        self.cash *= (1 + CDI) ** dt


# =========================
# Broker em memória
# =========================


@dataclass
class Fill:
    ticker: str
    price: float
    qty: float
    nav: float
    maker_involved: bool
    in_band: bool


class MemoryBroker(Broker):
    """Caixa e cotas por cliente; o formador segue o modelo escolhido."""

    def __init__(self, model: MakerModel, band: float) -> None:
        self.model = model
        self.band = band
        self.cash: dict[uuid.UUID, float] = {}
        self.position: dict[tuple[uuid.UUID, str], float] = {}
        self.funds: dict[str, Fund] = {}
        self.day_nav: dict[str, float] = {}
        self.fills: list[Fill] = []
        # Estoque e caixa sintético do formador, por ticker
        self.maker_stock: dict[str, float] = {}
        self.maker_cash: dict[str, float] = {}

    def holding(self, client: uuid.UUID, ticker: str) -> float:
        return self.position.get((client, ticker), 0.0)

    def _add_position(self, client: uuid.UUID, ticker: str, qty: float) -> None:
        self.position[(client, ticker)] = self.holding(client, ticker) + qty

    def reserve_limit_order(self, order: LimitOrder) -> None:
        if order.client_id == MAKER_ID:
            return
        qty = float(order.size)
        if order.action == OrderAction.BUY:
            cost = order.price * qty
            if self.cash.get(order.client_id, 0.0) < cost:
                raise InsufficentCashError()
            self.cash[order.client_id] -= cost
        else:
            if self.holding(order.client_id, order.ticker) < qty:
                raise InsufficentPositionError()
            self._add_position(order.client_id, order.ticker, -qty)

    def release_limit_order(self, order: LimitOrder) -> None:
        if order.client_id == MAKER_ID:
            return
        qty = float(order.remaining)
        if order.action == OrderAction.BUY:
            self.cash[order.client_id] += order.price * qty
        else:
            self._add_position(order.client_id, order.ticker, qty)

    def market_buy_limit(self, order: MarketOrder, price: float) -> Decimal:
        if order.client_id == MAKER_ID or order.action != OrderAction.BUY:
            return order.remaining
        affordable = math.floor(self.cash.get(order.client_id, 0.0) / price)
        return min(order.remaining, Decimal(affordable))

    def execute_trade(
        self,
        *,
        taker_order: Order,
        maker_order: LimitOrder,
        size: Decimal,
        price: float,
    ) -> None:
        qty = float(size)
        for order in (taker_order, maker_order):
            if order.client_id == MAKER_ID:
                self._maker_side(order, qty, price)
            else:
                self._player_side(order, qty, price)
        nav = self.day_nav[taker_order.ticker]
        involved = MAKER_ID in (taker_order.client_id, maker_order.client_id)
        in_band = nav * (1 - self.band) - CENT <= price <= nav * (1 + self.band) + CENT
        self.fills.append(Fill(taker_order.ticker, price, qty, nav, involved, in_band))

    def _player_side(self, order: Order, qty: float, price: float) -> None:
        client, ticker = order.client_id, order.ticker
        if order.action == OrderAction.BUY:
            if isinstance(order, LimitOrder):
                # A reserva foi pelo preço limite; a execução devolve a diferença
                self.cash[client] += (order.price - price) * qty
            else:
                if self.cash.get(client, 0.0) < price * qty - 1e-6:
                    raise InsufficentCashError()
                self.cash[client] -= price * qty
            self._add_position(client, ticker, qty)
        else:
            if isinstance(order, MarketOrder):
                if self.holding(client, ticker) < qty - 1e-9:
                    raise InsufficentPositionError()
                self._add_position(client, ticker, -qty)
            self.cash[client] = self.cash.get(client, 0.0) + price * qty

    def _maker_side(self, order: Order, qty: float, price: float) -> None:
        ticker = order.ticker
        buying = order.action == OrderAction.BUY
        if self.model == MakerModel.STOCK:
            self.maker_stock[ticker] += qty if buying else -qty
            self.maker_cash[ticker] += -price * qty if buying else price * qty
            return
        fund = self.funds[ticker]
        nav = self.day_nav[ticker]
        if buying:
            fund.quotas -= qty
            fund.cash -= price * qty
            fund.spread += (nav - price) * qty
        else:
            fund.quotas += qty
            fund.cash += price * qty
            fund.spread += (price - nav) * qty


# =========================
# Formador
# =========================


def _weights(shape: Shape, levels: int) -> np.ndarray:
    """Peso de cada nível, do mais perto ao mais longe do PL."""
    distance = np.arange(1, levels + 1) / levels
    match shape:
        case Shape.UNIFORM:
            raw = np.ones(levels)
        case Shape.EDGE:
            raw = distance
        case Shape.CENTER:
            raw = 1.05 - distance
    return raw / raw.sum()


class Maker:
    """Recalcula a cada dia as ordens de compra e venda em volta do PL de cada gestora."""

    def __init__(
        self, engine: MatchingEngine, broker: MemoryBroker, params: MakerParams
    ) -> None:
        self.engine = engine
        self.broker = broker
        self.params = params
        self.weights = _weights(params.shape, params.levels)
        self.orders: dict[str, list[LimitOrder]] = {}

    def refresh(self, ticker: str, nav: float, quotas: float, today: date) -> None:
        for order in self.orders.get(ticker, []):
            self.engine.order_book.remove(order)
        p = self.params
        side_qty = quotas * p.depth
        bids = self._ladder(ticker, nav, side_qty, OrderAction.BUY, today)
        asks = self._ladder(ticker, nav, side_qty, OrderAction.SELL, today)
        self.orders[ticker] = [*self._place(bids), *self._place(asks)]

    def _ladder(
        self, ticker: str, nav: float, side_qty: float, action: OrderAction, today: date
    ) -> list[LimitOrder]:
        p = self.params
        sign = -1 if action == OrderAction.BUY else 1
        budget = self._side_budget(ticker, action)
        orders: list[LimitOrder] = []
        for i, weight in enumerate(self.weights, start=1):
            price = round(nav * (1 + sign * p.band * i / p.levels), 2)
            qty = math.floor(side_qty * weight)
            cost = qty if action == OrderAction.SELL else qty * price
            if budget is not None:
                if cost > budget:
                    qty = math.floor(
                        budget if action == OrderAction.SELL else budget / price
                    )
                    cost = qty if action == OrderAction.SELL else qty * price
                budget -= cost
            if qty <= 0:
                continue
            orders.append(
                LimitOrder(
                    client_id=MAKER_ID,
                    ticker=ticker,
                    size=Decimal(qty),
                    action=action,
                    placed_on=today,
                    price=price,
                )
            )
        return orders

    def _side_budget(self, ticker: str, action: OrderAction) -> float | None:
        """Limite de cada lado: cotas para vender no estoque, caixa para resgatar na emissão."""
        if self.params.model == MakerModel.STOCK:
            return (
                self.broker.maker_stock[ticker] if action == OrderAction.SELL else None
            )
        return self.broker.funds[ticker].cash if action == OrderAction.BUY else None

    def _place(self, orders: list[LimitOrder]) -> list[LimitOrder]:
        placed: list[LimitOrder] = []
        book = self.engine.order_book
        for order in orders:
            if self.params.execution == Execution.CURRENT:
                if self.engine._process_market_order(order):
                    placed.append(order)
                continue
            opposite = (
                book.best_sell(order.ticker)
                if order.action == OrderAction.BUY
                else book.best_buy(order.ticker)
            )
            crosses = opposite is not None and (
                opposite.price <= order.price
                if order.action == OrderAction.BUY
                else opposite.price >= order.price
            )
            if not crosses:
                book.add(order)
                placed.append(order)
        return placed


# =========================
# Mercado e participantes
# =========================


@dataclass
class Candle:
    nav: float
    close: float
    vwap: float | None
    volume: float
    # Ágio do preço de ranking sobre o PL ao fim do pregão
    ranking: float = 0.0


class Market:
    def __init__(self, maker_params: MakerParams, funds: list[FundParams]) -> None:
        _silence_engine()
        self.broker = MemoryBroker(maker_params.model, maker_params.band)
        self.engine = MatchingEngine(self.broker)
        self.maker = Maker(self.engine, self.broker, maker_params)
        self.today = START
        self.candles: dict[str, list[Candle]] = {}
        for params in funds:
            fund = Fund.found(params)
            self.broker.funds[params.ticker] = fund
            self.broker.maker_stock[params.ticker] = 0.0
            self.broker.maker_cash[params.ticker] = 0.0
            self.candles[params.ticker] = []

    @property
    def tickers(self) -> list[str]:
        return list(self.broker.funds)

    def fund(self, ticker: str) -> Fund:
        return self.broker.funds[ticker]

    def open_day(self, rng: np.random.Generator) -> None:
        self.today += timedelta(days=1)
        self._fill_start = len(self.broker.fills)
        for ticker, fund in self.broker.funds.items():
            fund.advance(rng)
            self.broker.day_nav[ticker] = fund.nav
            fund.nav_history.append(fund.nav)
            self.maker.refresh(ticker, fund.nav, fund.quotas, self.today)

    def close_day(self) -> None:
        fills = self.broker.fills[self._fill_start :]
        for ticker in self.tickers:
            mine = [f for f in fills if f.ticker == ticker]
            nav = self.broker.day_nav[ticker]
            volume = sum(f.qty for f in mine)
            # Sem negócio, o fechamento repete o do pregão anterior, como na bolsa
            if mine:
                vwap = sum(f.price * f.qty for f in mine) / volume
                close = mine[-1].price
            else:
                vwap, close = None, self.last_close(ticker)
            self.candles[ticker].append(Candle(nav, close, vwap, volume))
            self.candles[ticker][-1].ranking = self.ranking_price(ticker) / nav - 1

    def submit(self, order: Order) -> float:
        """Envia a ordem e devolve quanto executou; ordem recusada executa zero."""
        try:
            self.engine.submit(order)
        except (ConflictError, InsufficentCashError, InsufficentPositionError):
            return 0.0
        return float(order.size - order.remaining)

    def limit(
        self,
        client: uuid.UUID,
        ticker: str,
        action: OrderAction,
        qty: float,
        price: float,
    ) -> LimitOrder:
        return LimitOrder(
            client_id=client,
            ticker=ticker,
            size=Decimal(qty),
            action=action,
            placed_on=self.today,
            price=round(price, 2),
        )

    def market(
        self, client: uuid.UUID, ticker: str, action: OrderAction, qty: float
    ) -> MarketOrder:
        return MarketOrder(
            client_id=client,
            ticker=ticker,
            size=Decimal(qty),
            action=action,
            placed_on=self.today,
        )

    def cancel_all(self, client: uuid.UUID) -> None:
        self.engine.cancel_all(client)

    def last_close(self, ticker: str) -> float:
        candles = self.candles[ticker]
        return candles[-1].close if candles else self.fund(ticker).nav

    def ranking_price(self, ticker: str, window: int = 20, cap: float = 0.30) -> float:
        """VWAP dos últimos pregões, travado em volta do PL; sem negócio, o PL."""
        candles = self.candles[ticker][-window:]
        nav = self.broker.day_nav[ticker]
        volume = sum(c.volume for c in candles)
        if volume == 0:
            return nav
        vwap = sum((c.vwap or 0.0) * c.volume for c in candles) / volume
        return min(max(vwap, nav * (1 - cap)), nav * (1 + cap))

    def raw_vwap(self, ticker: str, window: int = 20) -> float | None:
        candles = self.candles[ticker][-window:]
        volume = sum(c.volume for c in candles)
        if volume == 0:
            return None
        return sum((c.vwap or 0.0) * c.volume for c in candles) / volume


@dataclass
class Agent:
    """Participante que age uma vez por pregão."""

    name: str
    cash: float = 100_000.0
    is_bot: bool = False
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    attempts: int = 0
    filled: int = 0

    def join(self, market: Market) -> None:
        market.broker.cash[self.id] = self.cash

    def act(self, market: Market, rng: np.random.Generator) -> None:
        raise NotImplementedError

    def buy_cap(self, market: Market, ticker: str, qty: float) -> float:
        """Bot fica com no máximo 20% das cotas da gestora."""
        if not self.is_bot:
            return qty
        room = 0.20 * market.fund(ticker).quotas - market.broker.holding(
            self.id, ticker
        )
        return max(0.0, min(qty, math.floor(room)))

    def free_quotas(self, market: Market, ticker: str) -> float:
        return market.broker.holding(self.id, ticker)


@dataclass
class Holder(Agent):
    """O gestor ou um cotista que só segura."""

    def act(self, market: Market, rng: np.random.Generator) -> None:
        return None


@dataclass
class SteadyBuyer(Agent):
    """Quer uma quantidade fixa por pregão e paga até 3% acima do último fechamento; o que
    não executou no dia é cancelado e volta no dia seguinte, pelo novo fechamento."""

    ticker: str = ""
    qty: float = 10
    step: float = 0.03
    wanted: float = 0.0
    got: float = 0.0

    def act(self, market: Market, rng: np.random.Generator) -> None:
        market.cancel_all(self.id)
        qty = self.buy_cap(market, self.ticker, self.qty)
        if qty <= 0:
            return
        price = market.last_close(self.ticker) * (1 + self.step)
        self.wanted += qty
        self.got += market.submit(
            market.limit(self.id, self.ticker, OrderAction.BUY, qty, price)
        )


@dataclass
class EagerBuyer(Agent):
    """Deixa no livro uma compra limitada muito acima do PL, maior que a profundidade."""

    ticker: str = ""
    qty: float = 60
    premium: float = 1.0

    def act(self, market: Market, rng: np.random.Generator) -> None:
        nav = market.fund(self.ticker).nav
        market.cancel_all(self.id)
        price = nav * (1 + self.premium)
        qty = min(self.qty, math.floor(market.broker.cash[self.id] / price))
        if qty > 0:
            market.submit(
                market.limit(self.id, self.ticker, OrderAction.BUY, qty, price)
            )


@dataclass
class Noise(Agent):
    """Põe uma ordem limitada em volta do último preço e a cancela no dia seguinte."""

    ticker: str = ""
    qty: float = 5
    spread: float = 0.03
    activity: float = 0.5

    def act(self, market: Market, rng: np.random.Generator) -> None:
        market.cancel_all(self.id)
        if rng.random() > self.activity:
            return
        price = market.last_close(self.ticker) * (1 + rng.normal(0, self.spread))
        if rng.random() < 0.5:
            qty = self.buy_cap(market, self.ticker, self.qty)
            action = OrderAction.BUY
        else:
            qty = min(self.qty, self.free_quotas(market, self.ticker))
            action = OrderAction.SELL
        if qty > 0:
            market.submit(market.limit(self.id, self.ticker, action, qty, price))


@dataclass
class TwoRoomFriend(Agent):
    """Na sala de 2, o amigo do gestor compra ou vende 10 cotas a mercado por dia."""

    ticker: str = ""
    qty: float = 10
    buys: int = 0
    buys_filled: int = 0
    sells: int = 0
    sells_filled: int = 0

    def act(self, market: Market, rng: np.random.Generator) -> None:
        if rng.random() < 0.5:
            self.buys += 1
            order = market.market(self.id, self.ticker, OrderAction.BUY, self.qty)
            self.buys_filled += market.submit(order) > 0
            return
        qty = min(self.qty, self.free_quotas(market, self.ticker))
        if qty <= 0:
            return
        self.sells += 1
        order = market.market(self.id, self.ticker, OrderAction.SELL, qty)
        self.sells_filled += market.submit(order) > 0


@dataclass
class Follower(Agent):
    """Segue o desempenho publicado: compra quando o PL bate o CDI em 60 pregões e vende
    quando perde, sempre com ordem limitada até 5% acima do último preço."""

    lookback: int = 60
    cash_pct: float = 0.10

    def act(self, market: Market, rng: np.random.Generator) -> None:
        market.cancel_all(self.id)
        for ticker in market.tickers:
            history = market.fund(ticker).nav_history
            if len(history) <= self.lookback or rng.random() > 0.3:
                continue
            ret = history[-1] / history[-1 - self.lookback] - 1
            hurdle = (1 + CDI) ** (self.lookback / TRADING_DAYS) - 1
            last = market.last_close(ticker)
            if ret > hurdle:
                price = last * 1.05
                budget = market.broker.cash[self.id] * self.cash_pct
                qty = self.buy_cap(market, ticker, math.floor(budget / price))
                if qty > 0:
                    order = market.limit(self.id, ticker, OrderAction.BUY, qty, price)
                    market.submit(order)
            else:
                qty = math.floor(self.free_quotas(market, ticker) / 2)
                if qty > 0:
                    order = market.limit(
                        self.id, ticker, OrderAction.SELL, qty, last * 0.95
                    )
                    market.submit(order)


@dataclass
class BuyAndHoldBot(Agent):
    """Comprar e segurar: monta a posição no primeiro dia, a mercado, completando nos dias
    seguintes o que o livro não deu, e não vende."""

    ticker: str = ""
    cash_pct: float = 0.5
    target: float | None = None

    def act(self, market: Market, rng: np.random.Generator) -> None:
        if self.target is None:
            price = market.last_close(self.ticker)
            self.target = math.floor(self.cash * self.cash_pct / price)
        missing = self.target - market.broker.holding(self.id, self.ticker)
        qty = self.buy_cap(market, self.ticker, missing)
        if qty > 0:
            market.submit(market.market(self.id, self.ticker, OrderAction.BUY, qty))


def _rsi(closes: list[float], period: int) -> float | None:
    if len(closes) <= period:
        return None
    deltas = np.diff(np.array(closes[-period - 1 :]))
    gain = deltas[deltas > 0].sum() / period
    loss = -deltas[deltas < 0].sum() / period
    if loss == 0:
        return 100.0
    return 100 - 100 / (1 + gain / loss)


@dataclass
class SignalBot(Agent):
    """Bot de sinal sobre o fechamento da cota: cruzamento de médias ou IFR, como as
    estratégias reais; compra com 20% do caixa e vende tudo no sinal de saída."""

    ticker: str = ""
    kind: str = "ifr"
    cash_pct: float = 0.20

    def act(self, market: Market, rng: np.random.Generator) -> None:
        closes = [c.close for c in market.candles[self.ticker]]
        signal = self._signal(closes)
        if signal is None:
            return
        last = closes[-1]
        if signal == OrderAction.BUY:
            qty = self.buy_cap(
                market,
                self.ticker,
                math.floor(market.broker.cash[self.id] * self.cash_pct / last),
            )
        else:
            qty = self.free_quotas(market, self.ticker)
        if qty > 0:
            market.submit(market.market(self.id, self.ticker, signal, qty))

    def _signal(self, closes: list[float]) -> OrderAction | None:
        if self.kind == "ifr":
            rsi = _rsi(closes, 14)
            if rsi is None:
                return None
            if rsi < 30:
                return OrderAction.BUY
            if rsi > 70:
                return OrderAction.SELL
            return None
        # Médias de 20 e 50 pregões: as de 50 e 200 da estratégia real mal cruzam num ano
        if len(closes) < 51:
            return None
        fast_now, slow_now = np.mean(closes[-20:]), np.mean(closes[-50:])
        fast_prev, slow_prev = np.mean(closes[-21:-1]), np.mean(closes[-51:-1])
        if fast_prev <= slow_prev and fast_now > slow_now:
            return OrderAction.BUY
        if fast_prev >= slow_prev and fast_now < slow_now:
            return OrderAction.SELL
        return None


# =========================
# Rodadas
# =========================


def _setup(
    maker: MakerParams, funds: list[FundParams], agents: list[Agent]
) -> tuple[Market, list[Agent]]:
    market = Market(maker, funds)
    for agent in agents:
        agent.join(market)
    return market, agents


def _found(
    market: Market, manager: Agent, ticker: str, offer: list[tuple[Agent, float]]
) -> None:
    """O gestor funda com todas as cotas e a oferta pública vende cotas novas pelo PL."""
    fund = market.fund(ticker)
    market.broker.position[(manager.id, ticker)] = fund.quotas
    for agent, qty in offer:
        cost = qty * fund.nav
        market.broker.cash[agent.id] -= cost
        market.broker.position[(agent.id, ticker)] = (
            market.broker.holding(agent.id, ticker) + qty
        )
        fund.cash += cost
        fund.quotas += qty
    # O formador de estoque próprio subscreve a parte dele na oferta, pagando com caixa sintético
    params = market.maker.params
    if params.model == MakerModel.STOCK:
        qty = math.floor(fund.quotas * params.stock_share)
        fund.cash += qty * fund.nav
        fund.quotas += qty
        market.broker.maker_stock[ticker] += qty
        market.broker.maker_cash[ticker] -= qty * fund.nav


def _run(
    market: Market, agents: list[Agent], days: int, rng: np.random.Generator
) -> None:
    for _ in range(days):
        market.open_day(rng)
        for index in rng.permutation(len(agents)):
            agents[index].act(market, rng)
        market.close_day()


def _ranking_premiums(market: Market, ticker: str, skip: int = 0) -> list[float]:
    """Ágio do preço de ranking em cada pregão: preço ÷ PL - 1 (negativo é deságio)."""
    return [c.ranking for c in market.candles[ticker][skip:]]


def _trade_premiums(market: Market, ticker: str) -> tuple[np.ndarray, np.ndarray]:
    """Ágio de cada negócio sobre o PL do dia, com a quantidade de cada um."""
    fills = [f for f in market.broker.fills if f.ticker == ticker]
    return (
        np.array([f.price / f.nav - 1 for f in fills]),
        np.array([f.qty for f in fills]),
    )


def _maker_outside(market: Market) -> int:
    return sum(1 for f in market.broker.fills if f.maker_involved and not f.in_band)


def no_demand(
    maker: MakerParams, rng: np.random.Generator, days: int
) -> dict[str, float]:
    manager = Holder("gestor")
    noise = [Noise(f"ruido{i}", ticker=GOOD.ticker, activity=0.3) for i in range(2)]
    market, agents = _setup(maker, [GOOD], [manager, *noise])
    _found(market, manager, GOOD.ticker, [(n, 50) for n in noise])
    _run(market, agents, days, rng)
    premiums, qty = _trade_premiums(market, GOOD.ticker)
    traded = [c.volume > 0 for c in market.candles[GOOD.ticker]]
    ranking = np.abs(_ranking_premiums(market, GOOD.ticker))
    return {
        "mean_abs": float(np.average(np.abs(premiums), weights=qty))
        if qty.size
        else 0.0,
        "max_abs": float(np.abs(premiums).max()) if qty.size else 0.0,
        "ranking_abs": float(ranking.mean()),
        "traded_days": float(np.mean(traded)),
        "outside": _maker_outside(market),
    }


def steady_buying(
    maker: MakerParams, rng: np.random.Generator, days: int, qty: float = 10
) -> dict[str, float]:
    manager = Holder("gestor")
    buyer = SteadyBuyer("comprador", cash=10_000_000, ticker=GOOD.ticker, qty=qty)
    holders = [Noise(f"cotista{i}", ticker=GOOD.ticker, activity=0.3) for i in range(3)]
    market, agents = _setup(maker, [GOOD], [manager, buyer, *holders])
    _found(market, manager, GOOD.ticker, [(h, 100) for h in holders])
    _run(market, agents, days, rng)
    candles = market.candles[GOOD.ticker]
    daily = [c.vwap / c.nav - 1 if c.vwap else None for c in candles]
    edge = next(
        (
            i + 1
            for i, p in enumerate(daily)
            if p is not None and p >= maker.band * 0.95
        ),
        None,
    )
    ranking = _ranking_premiums(market, GOOD.ticker)
    traded = [p for p in daily if p is not None]
    return {
        "ranking_day20": ranking[19],
        "ranking_end": ranking[-1],
        "trade_max": float(max(traded, default=0.0)),
        "days_to_edge": float(edge) if edge else float("nan"),
        "buyer_fill_rate": buyer.got / max(buyer.wanted, 1),
        "outside": _maker_outside(market),
    }


def eager_buyer(
    maker: MakerParams, rng: np.random.Generator, days: int
) -> dict[str, float]:
    """Uma compra limitada a 2x o PL, maior que a profundidade, fica no livro de um dia para
    o outro: na execução de hoje, o formador que chega no dia seguinte vende a ela."""
    manager = Holder("gestor")
    eager = EagerBuyer("afobado", cash=10_000_000, ticker=GOOD.ticker)
    market, agents = _setup(maker, [GOOD], [manager, eager])
    _found(market, manager, GOOD.ticker, [])
    # O formador de estoque precisa de cotas para vender: o gestor vende a ele por 10 pregões
    for _ in range(10):
        market.open_day(rng)
        market.submit(market.market(manager.id, GOOD.ticker, OrderAction.SELL, 20))
        market.close_day()
    _run(market, agents, days, rng)
    maker_fills = [f for f in market.broker.fills if f.maker_involved]
    return {
        "outside": _maker_outside(market),
        "maker_fills": len(maker_fills),
        "worst_ratio": max((f.price / f.nav for f in maker_fills), default=1.0),
    }


def forced_trade(
    maker: MakerParams, rng: np.random.Generator, days: int
) -> dict[str, float]:
    """Dois jogadores combinam 10 cotas a 10x o PL; o comprador limpa antes as ofertas do
    formador que estão abaixo, para o negócio sair entre os dois."""
    manager = Holder("gestor")
    seller = Holder("vendedor")
    buyer = Holder("comprador", cash=10_000_000)
    noise = [Noise(f"ruido{i}", ticker=GOOD.ticker, activity=0.3) for i in range(2)]
    market, agents = _setup(maker, [GOOD], [manager, seller, buyer, *noise])
    _found(market, manager, GOOD.ticker, [(seller, 50), *[(n, 50) for n in noise]])
    _run(market, agents, 10, rng)
    market.open_day(rng)
    nav = market.fund(GOOD.ticker).nav
    price = nav * 10
    market.submit(market.limit(seller.id, GOOD.ticker, OrderAction.SELL, 10, price))
    below = sum(
        float(o.remaining)
        for o in market.engine.order_book.get_orders(GOOD.ticker)
        if o.action == OrderAction.SELL
        and isinstance(o, LimitOrder)
        and o.price < price
    )
    market.submit(
        market.limit(buyer.id, GOOD.ticker, OrderAction.BUY, below + 10, price)
    )
    market.close_day()
    ranking = market.ranking_price(GOOD.ticker) / nav
    raw = (market.raw_vwap(GOOD.ticker) or nav) / nav
    _run(market, agents, days, rng)
    return {
        "raw_vwap_ratio": raw,
        "ranking_ratio": ranking,
        "outside": _maker_outside(market),
    }


def two_room(
    maker: MakerParams, rng: np.random.Generator, days: int
) -> dict[str, float]:
    manager = Holder("gestor")
    friend = TwoRoomFriend("amigo", ticker=GOOD.ticker)
    market, agents = _setup(maker, [GOOD], [manager, friend])
    _found(market, manager, GOOD.ticker, [(friend, 200)])
    start_quotas = market.fund(GOOD.ticker).quotas
    _run(market, agents, days, rng)
    fund = market.fund(GOOD.ticker)
    return {
        "buy_fill_rate": friend.buys_filled / max(friend.buys, 1),
        "sell_fill_rate": friend.sells_filled / max(friend.sells, 1),
        "quota_change": fund.quotas / start_quotas - 1,
        "maker_stock": market.broker.maker_stock[GOOD.ticker],
        "maker_cash": market.broker.maker_cash[GOOD.ticker],
        "outside": _maker_outside(market),
    }


def full_match(
    maker: MakerParams, rng: np.random.Generator, days: int
) -> dict[str, float]:
    good_manager, bad_manager = Holder("gestor-bom"), Holder("gestor-ruim")
    followers = [Follower(f"seguidor{i}") for i in range(3)]
    noise = [
        Noise(f"ruido-{f.ticker}-{i}", ticker=f.ticker, activity=0.4)
        for f in (GOOD, BAD)
        for i in range(2)
    ]
    bots: list[Agent] = []
    for fund in (GOOD, BAD):
        bots += [
            BuyAndHoldBot(f"bh-{fund.ticker}", is_bot=True, ticker=fund.ticker),
            SignalBot(
                f"ifr-{fund.ticker}", is_bot=True, ticker=fund.ticker, kind="ifr"
            ),
            SignalBot(f"mm-{fund.ticker}", is_bot=True, ticker=fund.ticker, kind="mm"),
        ]
    everyone = [good_manager, bad_manager, *followers, *noise, *bots]
    market, agents = _setup(maker, [GOOD, BAD], everyone)
    offer_takers = [*followers, *noise]
    _found(market, good_manager, GOOD.ticker, [(a, 50) for a in offer_takers])
    _found(market, bad_manager, BAD.ticker, [(a, 50) for a in offer_takers])
    start = {t: market.fund(t).quotas for t in market.tickers}
    _run(market, agents, days, rng)
    result: dict[str, float] = {"outside": _maker_outside(market)}
    for label, ticker in (("good", GOOD.ticker), ("bad", BAD.ticker)):
        premiums = _ranking_premiums(market, ticker, skip=days // 2)
        ranking = market.ranking_price(ticker) / market.broker.day_nav[ticker] - 1
        bot_share = max(
            market.broker.holding(b.id, ticker) / market.fund(ticker).quotas
            for b in bots
        )
        result |= {
            f"{label}_premium": float(np.mean(premiums)),
            f"{label}_ranking_premium": ranking,
            f"{label}_nav_return": market.fund(ticker).nav / 100 - 1,
            f"{label}_spread_nav": market.fund(ticker).spread
            / market.fund(ticker).quotas
            / 100,
            f"{label}_quota_change": market.fund(ticker).quotas / start[ticker] - 1,
            f"{label}_max_bot_share": bot_share,
            f"{label}_traded_days": float(
                np.mean([c.volume > 0 for c in market.candles[ticker]])
            ),
        }
    return result


Scenario = Callable[[MakerParams, np.random.Generator, int], dict[str, float]]


def repeat(
    scenario: Scenario, maker: MakerParams, runs: int, seed: int, days: int
) -> dict[str, Any]:
    """Média de cada métrica em `runs` rodadas; `outside` é a soma, e `runs` vai junto."""
    rows = [scenario(maker, np.random.default_rng(seed + i), days) for i in range(runs)]
    summary: dict[str, Any] = {"runs": runs}
    for key in rows[0]:
        values = np.array([row[key] for row in rows], dtype=float)
        if key == "outside":
            summary[key] = int(values.sum())
        elif key == "days_to_edge":
            reached = values[~np.isnan(values)]
            summary["reached_edge"] = len(reached)
            summary[key] = float(np.median(reached)) if len(reached) else None
        elif key == "max_abs" or key.endswith("max_bot_share") or key == "worst_ratio":
            summary[key] = float(values.max())
        else:
            summary[key] = float(values.mean())
    return summary


BANDS = (0.10, 0.15, 0.20, 0.25, 0.30)
DEPTHS = (0.005, 0.01, 0.02, 0.05)


def answer(runs: int, seed: int) -> dict[str, Any]:
    base = MakerParams()
    models = (MakerModel.STOCK, MakerModel.ISSUANCE)
    grid: list[dict[str, Any]] = []
    for model in models:
        for shape in Shape:
            for band in BANDS:
                for depth in DEPTHS:
                    maker = replace(
                        base, model=model, shape=shape, band=band, depth=depth
                    )
                    grid.append(
                        {
                            "model": model.value,
                            "shape": shape.value,
                            "band": band,
                            "depth": depth,
                            "no_demand": repeat(no_demand, maker, runs, seed, 120),
                            "steady": repeat(steady_buying, maker, runs, seed, 120),
                        }
                    )
    by_model: dict[str, Any] = {}
    for model in models:
        maker = replace(base, model=model)
        by_model[model.value] = {
            "eager": {
                execution.value: repeat(
                    eager_buyer, replace(maker, execution=execution), runs, seed, 30
                )
                for execution in Execution
            },
            "forced": repeat(forced_trade, maker, runs, seed, 30),
            "two_room": repeat(two_room, maker, runs, seed, 250),
            "match": repeat(full_match, maker, runs, seed, 250),
        }
    return {"grid": grid, "by_model": by_model}


def _pct(value: float | None) -> str:
    return "—" if value is None else f"{value:+.1%}"


def report(answers: dict[str, Any]) -> None:
    grid = answers["grid"]
    runs = grid[0]["no_demand"]["runs"]
    print(f"Grade da faixa e da profundidade ({runs} rodadas por célula, 120 pregões)")
    print(
        "  sem procura: desvio médio dos negócios em relação ao PL (|preço ÷ PL - 1|)"
    )
    print(
        "  compra contínua de 10 cotas/dia: ágio do preço de ranking no 20º pregão e no"
    )
    print("  último, fração da compra que executou e pregões até negociar na borda")
    for model in (MakerModel.STOCK, MakerModel.ISSUANCE):
        for shape in Shape:
            print(f"\n  [{model.value} · {shape.value}]")
            print(
                "   faixa  prof.  desvio  ranking-20  ranking-fim  executou  borda(dias, n)"
            )
            for cell in grid:
                if cell["model"] != model.value or cell["shape"] != shape.value:
                    continue
                nd, st = cell["no_demand"], cell["steady"]
                edge = st["days_to_edge"]
                print(
                    f"   {cell['band']:>4.0%}  {cell['depth']:>5.1%}  "
                    f"{nd['mean_abs']:>6.1%}  {_pct(st['ranking_day20']):>10}  "
                    f"{_pct(st['ranking_end']):>11}  {st['buyer_fill_rate']:>8.0%}  "
                    f"{'—' if edge is None else f'{edge:.0f}'} "
                    f"({st['reached_edge']} de {runs})"
                )
    for model, data in answers["by_model"].items():
        print(f"\n[{model}] faixa 20%, profundidade 2%, uniforme")
        for execution, eager in data["eager"].items():
            print(
                f"  (3) execução {execution}: {eager['outside']} negócios do formador "
                f"fora da faixa em {eager['runs']} rodadas; pior preço "
                f"{eager['worst_ratio']:.2f}x o PL"
            )
        forced = data["forced"]
        print(
            f"  (4) negócio forçado a 10x o PL: VWAP de 20 pregões {forced['raw_vwap_ratio']:.2f}x"
            f" o PL; preço de ranking {forced['ranking_ratio']:.2f}x"
        )
        room = data["two_room"]
        print(
            f"  (5) sala de 2: compra a mercado achou contraparte em "
            f"{room['buy_fill_rate']:.0%} dos dias, venda em {room['sell_fill_rate']:.0%}"
        )
        print(
            f"  (6) cotas da gestora {_pct(room['quota_change'])}; estoque do formador "
            f"{room['maker_stock']:.0f} cotas, caixa sintético R$ {room['maker_cash']:,.0f}"
        )
        match = data["match"]
        print(
            f"  (7) partida de {match['runs']}: gestor bom PL {_pct(match['good_nav_return'])},"
            f" ágio de ranking médio no 2º semestre {_pct(match['good_premium'])}, no fim "
            f"{_pct(match['good_ranking_premium'])}; gestor ruim PL "
            f"{_pct(match['bad_nav_return'])}, {_pct(match['bad_premium'])} e "
            f"{_pct(match['bad_ranking_premium'])}"
        )
        print(
            f"      do PL, vindo da emissão acima e do resgate abaixo do PL: "
            f"{_pct(match['good_spread_nav'])} e {_pct(match['bad_spread_nav'])}"
        )
        print(
            f"      bot com mais cotas: {match['good_max_bot_share']:.0%} e "
            f"{match['bad_max_bot_share']:.0%}; pregões com negócio "
            f"{match['good_traded_days']:.0%} e {match['bad_traded_days']:.0%}; "
            f"cotas {_pct(match['good_quota_change'])} e {_pct(match['bad_quota_change'])}; "
            f"formador fora da faixa: {match['outside']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    # O terminal do Windows abre em cp1252, que não tem o sinal de menos nem o ÷
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    result = answer(args.runs, args.seed)
    if args.out:
        args.out.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    report(result)


if __name__ == "__main__":
    main()
