from __future__ import annotations

import logging
from collections import defaultdict
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
from backend.features.variable_income.entities.order import LimitOrder, OrderAction
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
        self._reserved_cash_by_order: dict[str, float] = {}
        self._reserved_position_by_order: dict[str, int] = {}
        self._reserved_positions: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

    def get_positions(self, client_id: str) -> dict[str, Position]:
        return self._positions[client_id]

    def reserve_limit_order(self, order: LimitOrder) -> None:
        if order.client_id == MarketLiquidity.MARKET_CLIENT_ID:
            return

        if order.action == OrderAction.BUY:
            cost = order.price * order.size
            if self._simulation_engine.get_cash(order.client_id) < cost:
                raise InsufficentCashError()

            self._simulation_engine.add_cash(order.client_id, -cost)
            self._reserved_cash_by_order[order.id] = cost
            return

        available = self._available_position(order.client_id, order.ticker)
        if available < order.size:
            raise InsufficentPositionError()

        self._reserved_position_by_order[order.id] = order.size
        self._reserved_positions[order.client_id][order.ticker] += order.size

    def release_limit_order(self, order: LimitOrder) -> None:
        if order.client_id == MarketLiquidity.MARKET_CLIENT_ID:
            return

        if order.action == OrderAction.BUY:
            reserved = self._reserved_cash_by_order.pop(order.id, 0.0)
            if reserved > 0:
                self._simulation_engine.add_cash(order.client_id, reserved)
            return

        reserved_qty = self._reserved_position_by_order.pop(order.id, 0)
        if reserved_qty <= 0:
            return

        self._reserved_positions[order.client_id][order.ticker] -= reserved_qty
        if self._reserved_positions[order.client_id][order.ticker] <= 0:
            self._reserved_positions[order.client_id].pop(order.ticker, None)

    def execute_trade_atomic(
        self,
        *,
        taker_client_id: str,
        maker_client_id: str,
        ticker: str,
        size: int,
        price: float,
        taker_action: OrderAction,
        maker_action: OrderAction,
        taker_use_reserved: bool = False,
        maker_use_reserved: bool = False,
        taker_order_id: str | None = None,
        maker_order_id: str | None = None,
        taker_limit_price: float | None = None,
        maker_limit_price: float | None = None,
    ) -> None:
        """Executa uma trade atomicamente entre taker e maker.

        Se maker_client_id for MARKET_CLIENT_ID, faz bypass (sem evento/notificação).
        Se ambos forem clientes reais, valida ambos ANTES de executar qualquer coisa.
        Se validação falhar em qualquer um, nenhum é executado (atomicidade).
        """
        qty = size
        cost = price * qty
        if size <= 0:
            raise ValueError("Quantidade deve ser maior que zero")

        # =========================
        # VALIDAÇÃO DUPLA
        # =========================
        self.validate_trade_leg(
            client_id=maker_client_id,
            ticker=ticker,
            qty=qty,
            cost=cost,
            action=maker_action,
            use_reserved=maker_use_reserved,
            order_id=maker_order_id,
            limit_price=maker_limit_price,
        )
        self.validate_trade_leg(
            client_id=taker_client_id,
            ticker=ticker,
            qty=qty,
            cost=cost,
            action=taker_action,
            use_reserved=taker_use_reserved,
            order_id=taker_order_id,
            limit_price=taker_limit_price,
        )

        # =========================
        # EXECUÇÃO
        # =========================
        self.execute_trade(
            client_id=taker_client_id,
            ticker=ticker,
            size=qty,
            price=price,
            action=taker_action,
            use_reserved=taker_use_reserved,
            order_id=taker_order_id,
            limit_price=taker_limit_price,
        )
        self.execute_trade(
            client_id=maker_client_id,
            ticker=ticker,
            size=qty,
            price=price,
            action=maker_action,
            use_reserved=maker_use_reserved,
            order_id=maker_order_id,
            limit_price=maker_limit_price,
        )

    def execute_trade(
        self,
        *,
        client_id: str,
        ticker: str,
        size: int,
        price: float,
        action: OrderAction,
        use_reserved: bool = False,
        order_id: str | None = None,
        limit_price: float | None = None,
    ):
        # Executa a ordem para o cliente (se não for MARKET)
        if client_id != MarketLiquidity.MARKET_CLIENT_ID:
            match action:
                case OrderAction.BUY:
                    if use_reserved:
                        self._consume_reserved_buy(
                            client_id=client_id,
                            order_id=order_id,
                            limit_price=limit_price,
                            qty=size,
                            trade_price=price,
                        )
                        self._apply_buy_position(client_id, ticker, size, price)
                    else:
                        self._execute_buy(client_id, ticker, size, price)
                case OrderAction.SELL:
                    if use_reserved:
                        self._consume_reserved_sell(
                            client_id=client_id,
                            ticker=ticker,
                            order_id=order_id,
                            qty=size,
                        )
                    self._execute_sell(client_id, ticker, size, price)

    def validate_trade_leg(
        self,
        *,
        client_id: str,
        ticker: str,
        qty: int,
        cost: float,
        action: OrderAction,
        use_reserved: bool = False,
        order_id: str | None = None,
        limit_price: float | None = None,
    ):
        """Valida se o cliente pode executar a ordem. Se o cliente for MARKET, faz bypass."""
        if client_id == MarketLiquidity.MARKET_CLIENT_ID:
            return

        if action == OrderAction.SELL:
            if use_reserved:
                reserved_qty = self._reserved_position_by_order.get(order_id or "", 0)
                if reserved_qty < qty:
                    raise InsufficentPositionError()
                return

            if self._available_position(client_id, ticker) < qty:
                raise InsufficentPositionError()
            return

        if use_reserved:
            if limit_price is None:
                raise ValueError("limit_price é obrigatório para BUY reservado")
            required = limit_price * qty
            reserved_cash = self._reserved_cash_by_order.get(order_id or "", 0.0)
            if reserved_cash < required:
                raise InsufficentCashError()
            return

        if self._simulation_engine.get_cash(client_id) < cost:
            raise InsufficentCashError()

    def _available_position(self, client_id: str, ticker: str) -> int:
        position = self._positions[client_id].get(ticker)
        if not position:
            return 0

        reserved = self._reserved_positions[client_id].get(ticker, 0)
        return position.size - reserved

    def _execute_buy(self, client_id: str, ticker: str, size: int, price: float):
        cost = price * size

        self._simulation_engine.add_cash(client_id, -cost)

        self._apply_buy_position(client_id, ticker, size, price)

    def _apply_buy_position(
        self, client_id: str, ticker: str, size: int, price: float
    ) -> None:
        if ticker not in self._positions[client_id]:
            self._positions[client_id][ticker] = Position(ticker)

        self._positions[client_id][ticker].update_buy(price, size)

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

        notify(
            event=f"position_update:{ticker}",
            payload={
                "position": PositionDTO.from_model(
                    self._positions[client_id][ticker]
                ).to_json()
            },
            to=client_id,
        )
        logger.info(f"Executado BUY {size}x {ticker} @ R$ {price}")

    def _consume_reserved_buy(
        self,
        *,
        client_id: str,
        order_id: str | None,
        limit_price: float | None,
        qty: int,
        trade_price: float,
    ) -> None:
        if order_id is None or limit_price is None:
            raise ValueError("order_id e limit_price são obrigatórios")

        reserved_cost = limit_price * qty
        current_reserved = self._reserved_cash_by_order.get(order_id, 0.0)
        if current_reserved < reserved_cost:
            raise InsufficentCashError()

        self._reserved_cash_by_order[order_id] = current_reserved - reserved_cost
        if self._reserved_cash_by_order[order_id] <= 0:
            self._reserved_cash_by_order.pop(order_id, None)

        refund = reserved_cost - (trade_price * qty)
        if refund > 0:
            self._simulation_engine.add_cash(client_id, refund)

    def _consume_reserved_sell(
        self,
        *,
        client_id: str,
        ticker: str,
        order_id: str | None,
        qty: int,
    ) -> None:
        if order_id is None:
            raise ValueError("order_id é obrigatório")

        current_reserved = self._reserved_position_by_order.get(order_id, 0)
        if current_reserved < qty:
            raise InsufficentPositionError()

        self._reserved_position_by_order[order_id] = current_reserved - qty
        if self._reserved_position_by_order[order_id] <= 0:
            self._reserved_position_by_order.pop(order_id, None)

        self._reserved_positions[client_id][ticker] -= qty
        if self._reserved_positions[client_id][ticker] <= 0:
            self._reserved_positions[client_id].pop(ticker, None)

    def _execute_sell(self, client_id: str, ticker: str, size: int, price: float):
        pos = self._positions[client_id][ticker]
        self._simulation_engine.add_cash(client_id, price * size)
        pos.update_sell(size)

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

        notify(
            event=f"position_update:{ticker}",
            payload={
                "position": PositionDTO.from_model(
                    self._positions[client_id][ticker]
                ).to_json()
            },
            to=client_id,
        )
        if pos.size == 0:
            del self._positions[client_id][ticker]

        logger.info(f"Executado SELL {size}x {ticker} @ R$ {price}")
