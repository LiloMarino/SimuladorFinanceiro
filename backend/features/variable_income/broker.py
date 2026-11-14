from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from decimal import ROUND_DOWN, Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from backend.core import repository
from backend.core.dto.corporate_event import CorporateEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.enum import (
    AssetClass,
    CorporateEventKind,
    EquityEventType,
    OrderAction,
)
from backend.core.exceptions import InsufficentCashError, InsufficentPositionError
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils.lazy_dict import LazyDict
from backend.features.funds.fund_account import FundAccount
from backend.features.realtime import notify
from backend.features.realtime.schemas import PositionUpdateEventDTO
from backend.features.variable_income.corporate_actions import (
    DividendReceived,
    PlayerCorporateActions,
    SplitApplied,
)
from backend.features.variable_income.entities.order import (
    FUND_ISSUER_CLIENT_ID,
    FUND_MAKER_CLIENT_ID,
    MARKET_CLIENT_ID,
    LimitOrder,
    MarketOrder,
    Order,
)
from backend.features.variable_income.entities.position import Position

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine

logger = logging.getLogger(__name__)


CENT = Decimal("0.01")
# Quantidade negocia com oito casas, como a coluna dos eventos
QUANTITY_STEP = Decimal("1e-8")

# Contas sintéticas do motor: as ordens delas não reservam caixa nem posição
UNRESERVED_CLIENT_IDS = frozenset(
    {MARKET_CLIENT_ID, FUND_MAKER_CLIENT_ID, FUND_ISSUER_CLIENT_ID}
)


def to_money(price: float) -> Decimal:
    """Preço de ação (float na origem) em Decimal pelo texto, sem a expansão binária."""
    return Decimal(str(price))


def load_positions(client_id: UUID) -> dict[str, Position]:
    """Reconstrói as posições repetindo os eventos com as mesmas operações do jogo ao vivo."""
    portfolio_id = UserManager.get_portfolio_id(client_id)

    positions: dict[str, Position] = {}
    for event in repository.portfolio.get_equity_events(portfolio_id):
        position = positions.setdefault(event.ticker, Position(event.ticker))
        match event.event_type:
            case EquityEventType.BUY:
                position.update_buy(event.price, event.quantity)
            case EquityEventType.SELL | EquityEventType.FRACTION_SELL:
                position.update_sell(event.quantity)
            case EquityEventType.SPLIT:
                position.update_split(event.quantity)

    return {ticker: p for ticker, p in positions.items() if p.size > 0}


class Broker:
    """
    Gerenciador de posições de renda variável e execução de trades.

    Responsável por:
    - Manter posições dos players com cache lazy carregado do banco
    - Executar trades atomicamente entre taker e maker com validação dupla
    - Gerenciar cash flow (débito/crédito) em compras e vendas
    - Registrar eventos de equity (BUY, SELL, DIVIDEND) no EventManager
    - Emitir notificações realtime de atualizações de portfólio
    - Fazer bypass para ordens de liquidez sintética (MARKET_CLIENT_ID)
    - Mover o estado da gestora nos negócios do formador (FUND_MAKER_CLIENT_ID) e da
      oferta pública (FUND_ISSUER_CLIENT_ID), sem evento de ação nem reserva
    """

    def __init__(
        self,
        simulation_engine: SimulationEngine,
        lock: threading.RLock,
    ):
        self._simulation_engine = simulation_engine
        self._lock = lock
        self._positions: LazyDict[UUID, dict[str, Position]] = LazyDict(load_positions)
        # A gestora de cada cota negociada, pelo ticker
        self.fund_accounts: dict[str, FundAccount] = {}

    def get_positions(self, client_id: UUID) -> dict[str, Position]:
        with self._lock:
            return self._positions[client_id]

    def apply_corporate_events(
        self,
        events: list[CorporateEventDTO],
        tickers: dict[int, str],
        classes: dict[str, AssetClass],
        closes: dict[str, Decimal],
        client_ids: list[UUID],
    ) -> dict[UUID, PlayerCorporateActions]:
        """
        Aplica desdobramentos e dividendos à posição que cada jogador tem na abertura
        do dia. Na mesma data ex o desdobramento vem antes do dividendo: o valor por
        cota da data ex já está na unidade nova.
        """
        applied: dict[UUID, PlayerCorporateActions] = {}
        ordered = sorted(
            events,
            key=lambda e: (
                e.ex_date,
                e.stock_id,
                e.kind is not CorporateEventKind.SPLIT,
            ),
        )
        with self._lock:
            for event in ordered:
                ticker = tickers.get(event.stock_id)
                if ticker is None:
                    continue
                value = Decimal(str(event.value))
                for client_id in client_ids:
                    position = self._positions[client_id].get(ticker)
                    if position is None or position.size <= 0:
                        continue
                    actions = applied.setdefault(client_id, PlayerCorporateActions())
                    match event.kind:
                        case CorporateEventKind.SPLIT:
                            actions.splits.append(
                                self._apply_split(
                                    client_id,
                                    position,
                                    value,
                                    classes[ticker],
                                    closes.get(ticker, position.avg_price),
                                )
                            )
                        case CorporateEventKind.DIVIDEND:
                            dividend = self._pay_dividend(client_id, position, value)
                            if dividend is not None:
                                actions.dividends.append(dividend)
        return applied

    def _apply_split(
        self,
        client_id: UUID,
        position: Position,
        ratio: Decimal,
        asset_class: AssetClass,
        close: Decimal,
    ) -> SplitApplied:
        ticker = position.ticker
        size_before = position.size
        avg_before = position.avg_price
        delta = (size_before * ratio).quantize(QUANTITY_STEP) - size_before

        self._mutate_position(
            client_id=client_id,
            ticker=ticker,
            mutation=lambda p: p.update_split(delta),
        )
        self._push_equity_event(client_id, EquityEventType.SPLIT, ticker, delta, 0)

        # Classe de quantidade inteira: a fração que sobrou vira venda ao close do dia
        fraction = Decimal(0)
        if not asset_class.fractional:
            fraction = position.size - position.size.to_integral_value(ROUND_DOWN)
        if fraction > 0:
            self._simulation_engine.add_cash(client_id, close * fraction)
            self._mutate_position(
                client_id=client_id,
                ticker=ticker,
                mutation=lambda p: p.update_sell(fraction),
            )
            self._push_equity_event(
                client_id, EquityEventType.FRACTION_SELL, ticker, fraction, close
            )

        return SplitApplied(
            ticker=ticker,
            ratio=ratio,
            size_before=size_before,
            size_after=position.size,
            avg_price_before=avg_before,
            avg_price_after=position.avg_price,
            fraction_sold=fraction,
            fraction_amount=close * fraction,
        )

    def _pay_dividend(
        self, client_id: UUID, position: Position, per_share: Decimal
    ) -> DividendReceived | None:
        amount = (per_share * position.size).quantize(CENT, ROUND_DOWN)
        if amount <= 0:
            return None
        self._simulation_engine.pay_dividend(client_id, position.ticker, amount)
        return DividendReceived(position.ticker, per_share, position.size, amount)

    def _push_equity_event(
        self,
        client_id: UUID,
        event_type: EquityEventType,
        ticker: str,
        quantity: Decimal,
        price: Decimal | int,
    ) -> None:
        EventManager.push_event(
            EquityEventDTO(
                simulation_id=self._simulation_engine.simulation_id,
                portfolio_id=UserManager.get_portfolio_id(client_id),
                event_type=event_type,
                ticker=ticker,
                quantity=quantity,
                price=Decimal(price),
                event_date=self._simulation_engine.current_date,
            )
        )

    def get_available_position(self, client_id: UUID, ticker: str) -> Decimal:
        with self._lock:
            position = self._positions[client_id].get(ticker)
            if not position:
                return Decimal(0)
            return max(Decimal(0), position.size - position.reserved)

    def reserve_limit_order(self, order: LimitOrder) -> None:
        if order.client_id in UNRESERVED_CLIENT_IDS:
            return

        with self._lock:
            if order.action == OrderAction.BUY:
                cost = to_money(order.price) * order.size
                if self._simulation_engine.get_cash(order.client_id) < cost:
                    raise InsufficentCashError()

                self._simulation_engine.add_cash(order.client_id, -cost)

            elif order.action == OrderAction.SELL:
                position = self._positions[order.client_id].get(order.ticker)
                if not position:
                    raise InsufficentPositionError()

                self._mutate_position(
                    client_id=order.client_id,
                    ticker=order.ticker,
                    mutation=lambda p: p.reserve(order.size),
                )

    def release_limit_order(self, order: LimitOrder) -> None:
        if order.client_id in UNRESERVED_CLIENT_IDS:
            return

        with self._lock:
            if order.action == OrderAction.BUY:
                cost = to_money(order.price) * order.remaining
                self._simulation_engine.add_cash(order.client_id, cost)

            elif order.action == OrderAction.SELL:
                position = self._positions[order.client_id].get(order.ticker)
                if position:
                    self._mutate_position(
                        client_id=order.client_id,
                        ticker=order.ticker,
                        mutation=lambda p: p.release(order.remaining),
                    )

    def execute_trade(
        self,
        *,
        taker_order: Order,
        maker_order: LimitOrder,
        size: Decimal,
        price: float,
    ) -> None:
        """Executa uma trade entre taker e maker.

        Se maker_client_id for MARKET_CLIENT_ID, faz bypass (sem evento/notificação).
        Valida cash/posição para ordens de clientes reais (não MARKET) antes de executar.
        """
        if size <= 0:
            raise ValueError("Quantidade deve ser maior que zero")

        with self._lock:
            if isinstance(taker_order, MarketOrder):
                self._validate_market_order(taker_order, size, price)

            # =========================
            # EXECUÇÃO
            # =========================
            self._execute_order(
                order=taker_order,
                size=size,
                price=price,
            )
            self._execute_order(
                order=maker_order,
                size=size,
                price=price,
            )
            # Cada negócio da cota de gestora conta uma vez, para a vela e o giro do dia
            account = self.fund_accounts.get(taker_order.ticker)
            if account is not None:
                account.record_trade(size, to_money(price))

    def market_buy_limit(self, order: MarketOrder, price: float) -> Decimal:
        """Quanto a compra a mercado ainda pode comprar a este preço com o caixa e o valor da ordem.

        Só a boleta manual se ajusta ao caixa. Venda, ordem da liquidez do mercado e ordem de
        estratégia (que já traz a quantidade que ela decidiu) valem o `remaining`; a conferência
        da execução recusa a que não cabe.
        """
        if (
            order.client_id in UNRESERVED_CLIENT_IDS
            or order.action != OrderAction.BUY
            or order.automatic
        ):
            return order.remaining

        with self._lock:
            money = self._simulation_engine.get_cash(order.client_id)
            if order.budget is not None:
                money = min(money, order.budget)
            return min(
                order.remaining,
                self._simulation_engine.affordable(
                    order.ticker, money, to_money(price)
                ),
            )

    def _execute_order(
        self,
        order: Order,
        size: Decimal,
        price: float,
    ):
        if order.client_id == MARKET_CLIENT_ID:
            return
        if order.client_id == FUND_MAKER_CLIENT_ID:
            self.fund_accounts[order.ticker].maker_trade(
                order.action, size, to_money(price)
            )
            return
        if order.client_id == FUND_ISSUER_CLIENT_ID:
            self._execute_fund_offer(order, size, price)
            return
        match order.action:
            case OrderAction.BUY:
                self._execute_buy(order, size, price)
            case OrderAction.SELL:
                self._execute_sell(order, size, price)

    def _execute_fund_offer(self, order: Order, size: Decimal, price: float) -> None:
        """A venda da oferta emite as cotas e põe o dinheiro no caixa da gestora."""
        if order.action != OrderAction.SELL:
            raise ValueError("A oferta pública só vende")
        account = self.fund_accounts[order.ticker]
        account.issue(size)
        self._simulation_engine.credit_fund_offer(
            account.client_id, to_money(price) * size
        )

    def _validate_market_order(self, order: MarketOrder, size: Decimal, price: float):
        if order.client_id not in UNRESERVED_CLIENT_IDS:
            if (
                order.action == OrderAction.SELL
                and self.get_available_position(order.client_id, order.ticker) < size
            ):
                raise InsufficentPositionError()

            if (
                order.action == OrderAction.BUY
                and self._simulation_engine.get_cash(order.client_id)
                < to_money(price) * size
            ):
                raise InsufficentCashError()

    def _mutate_position(
        self,
        *,
        client_id: UUID,
        ticker: str,
        mutation: Callable[[Position], None],
    ):
        with self._lock:
            if ticker not in self._positions[client_id]:
                self._positions[client_id][ticker] = Position(ticker)

            position = self._positions[client_id][ticker]

            # Executa a mutação real (buy/sell/reserve/release)
            mutation(position)

            # Remove posição se zerou
            if position.size == 0 and position.reserved == 0:
                del self._positions[client_id][ticker]

            position_payload = PositionUpdateEventDTO(
                position=position.to_dto(
                    self._simulation_engine.get_current_price(position)
                )
            ).to_json()

        notify(
            event=f"position_update:{ticker}",
            payload=position_payload,
            to=client_id,
        )

    def _execute_buy(self, order: Order, size: Decimal, price: float):
        client_id = order.client_id
        ticker = order.ticker
        money_price = to_money(price)
        cost = money_price * size

        if isinstance(order, MarketOrder):
            self._simulation_engine.add_cash(client_id, -cost)

        if isinstance(order, LimitOrder):
            refund = (to_money(order.price) - money_price) * size
            self._simulation_engine.add_cash(client_id, refund)

        self._mutate_position(
            client_id=client_id,
            ticker=ticker,
            mutation=lambda p: p.update_buy(money_price, size),
        )

        EventManager.push_event(
            EquityEventDTO(
                simulation_id=self._simulation_engine.simulation_id,
                portfolio_id=UserManager.get_portfolio_id(client_id),
                event_type=EquityEventType.BUY,
                ticker=ticker,
                quantity=size,
                price=to_money(price),
                event_date=self._simulation_engine.current_date,
            )
        )

        logger.debug("Compra executada: %sx %s a R$ %s", size, ticker, price)

    def _execute_sell(self, order: Order, size: Decimal, price: float):
        client_id = order.client_id
        ticker = order.ticker

        self._simulation_engine.add_cash(client_id, to_money(price) * size)

        def _sell_mutation(p: Position):
            if isinstance(order, LimitOrder):
                p.release(size)
            p.update_sell(size)

        self._mutate_position(
            client_id=client_id,
            ticker=ticker,
            mutation=_sell_mutation,
        )

        EventManager.push_event(
            EquityEventDTO(
                simulation_id=self._simulation_engine.simulation_id,
                portfolio_id=UserManager.get_portfolio_id(client_id),
                event_type=EquityEventType.SELL,
                ticker=ticker,
                quantity=size,
                price=to_money(price),
                event_date=self._simulation_engine.current_date,
            )
        )

        logger.debug("Venda executada: %sx %s a R$ %s", size, ticker, price)
