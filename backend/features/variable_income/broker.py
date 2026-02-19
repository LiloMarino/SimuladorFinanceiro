from __future__ import annotations

import logging
from collections.abc import Callable
from decimal import Decimal
from typing import TYPE_CHECKING

from backend.core import repository
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.position import PositionDTO
from backend.core.enum import EquityEventType
from backend.core.exceptions import InsufficentCashError, InsufficentPositionError
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils.lazy_dict import LazyDict
from backend.features.realtime import notify
from backend.features.variable_income.entities.order import (
    LimitOrder,
    MarketOrder,
    Order,
    OrderAction,
)
from backend.features.variable_income.entities.position import Position
from backend.features.variable_income.market_liquidity import MarketLiquidity

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine

logger = logging.getLogger(__name__)


def load_positions(client_id: str) -> dict[str, Position]:
    user_id = UserManager.get_user_id(client_id)

    dtos = repository.portfolio.get_equity_positions(user_id)

    positions: dict[str, Position] = {}

    for dto in dtos:
        positions[dto.ticker] = Position(
            ticker=dto.ticker,
            size=dto.size,
            total_cost=dto.total_cost,
            avg_price=dto.avg_price,
        )

    return positions


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
    """

    def __init__(
        self,
        simulation_engine: SimulationEngine,
    ):
        self._simulation_engine = simulation_engine
        self._positions: LazyDict[str, dict[str, Position]] = LazyDict(load_positions)

    def get_positions(self, client_id: str) -> dict[str, Position]:
        return self._positions[client_id]

    def get_available_position(self, client_id: str, ticker: str) -> int:
        position = self._positions[client_id].get(ticker)
        if not position:
            return 0
        return max(0, position.size - position.reserved)

    def reserve_limit_order(self, order: LimitOrder) -> None:
        if order.client_id == MarketLiquidity.MARKET_CLIENT_ID:
            return

        if order.action == OrderAction.BUY:
            cost = order.price * order.size
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
        if order.client_id == MarketLiquidity.MARKET_CLIENT_ID:
            return

        if order.action == OrderAction.BUY:
            cost = order.price * order.remaining
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
        size: int,
        price: float,
    ) -> None:
        """Executa uma trade entre taker e maker.

        Se maker_client_id for MARKET_CLIENT_ID, faz bypass (sem evento/notificação).
        Valida cash/posição para ordens de clientes reais (não MARKET) antes de executar.
        """
        if size <= 0:
            raise ValueError("Quantidade deve ser maior que zero")

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

    def _execute_order(
        self,
        order: Order,
        size: int,
        price: float,
    ):
        # Executa a ordem para o cliente (se não for MARKET)
        if order.client_id != MarketLiquidity.MARKET_CLIENT_ID:
            match order.action:
                case OrderAction.BUY:
                    self._execute_buy(order, size, price)
                case OrderAction.SELL:
                    self._execute_sell(order, size, price)

    def _validate_market_order(self, order: MarketOrder, size: int, price: float):
        if order.client_id != MarketLiquidity.MARKET_CLIENT_ID:
            if (
                order.action == OrderAction.SELL
                and self.get_available_position(order.client_id, order.ticker) < size
            ):
                raise InsufficentPositionError()

            if (
                order.action == OrderAction.BUY
                and self._simulation_engine.get_cash(order.client_id) < price * size
            ):
                raise InsufficentCashError()

    def _mutate_position(
        self,
        *,
        client_id: str,
        ticker: str,
        mutation: Callable[[Position], None],
    ):
        if ticker not in self._positions[client_id]:
            self._positions[client_id][ticker] = Position(ticker)

        position = self._positions[client_id][ticker]

        # Executa a mutação real (buy/sell/reserve/release)
        mutation(position)

        # Remove posição se zerou
        if position.size == 0 and position.reserved == 0:
            del self._positions[client_id][ticker]

        notify(
            event=f"position_update:{ticker}",
            payload={"position": PositionDTO.from_model(position).to_json()},
            to=client_id,
        )

    def _execute_buy(self, order: Order, size: int, price: float):
        client_id = order.client_id
        ticker = order.ticker
        cost = price * size

        if isinstance(order, MarketOrder):
            self._simulation_engine.add_cash(client_id, -cost)

        if isinstance(order, LimitOrder):
            refund = (order.price - price) * size
            self._simulation_engine.add_cash(client_id, refund)

        self._mutate_position(
            client_id=client_id,
            ticker=ticker,
            mutation=lambda p: p.update_buy(price, size),
        )

        EventManager.push_event(
            EquityEventDTO(
                user_id=UserManager.get_user_id(client_id),
                event_type=EquityEventType.BUY,
                ticker=ticker,
                quantity=size,
                price=Decimal(price),
                event_date=self._simulation_engine.current_date,
            )
        )

        logger.info(f"Executado BUY {size}x {ticker} @ R$ {price}")

    def _execute_sell(self, order: Order, size: int, price: float):
        client_id = order.client_id
        ticker = order.ticker

        self._simulation_engine.add_cash(client_id, price * size)

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
                user_id=UserManager.get_user_id(client_id),
                event_type=EquityEventType.SELL,
                ticker=ticker,
                quantity=size,
                price=Decimal(price),
                event_date=self._simulation_engine.current_date,
            )
        )

        logger.info(f"Executado SELL {size}x {ticker} @ R$ {price}")
