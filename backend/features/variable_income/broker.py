from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from backend.core import repository
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.position import PositionDTO
from backend.core.enum import EquityEventType
from backend.core.exceptions import InsufficentCashError, InsufficentPositionError
from backend.core.logger import setup_logger
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils.lazy_dict import LazyDict
from backend.features.realtime import notify
from backend.features.variable_income.entities.order import OrderAction
from backend.features.variable_income.entities.position import Position
from backend.features.variable_income.market_liquidity import MarketLiquidity

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine

logger = setup_logger(__name__)


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
        self._validate_order(
            client_id=maker_client_id,
            ticker=ticker,
            qty=qty,
            cost=cost,
            action=maker_action,
        )
        self._validate_order(
            client_id=taker_client_id,
            ticker=ticker,
            qty=qty,
            cost=cost,
            action=taker_action,
        )

        # =========================
        # EXECUÇÃO
        # =========================
        self._execute_order(
            client_id=taker_client_id,
            ticker=ticker,
            size=qty,
            price=price,
            action=taker_action,
        )
        self._execute_order(
            client_id=maker_client_id,
            ticker=ticker,
            size=qty,
            price=price,
            action=maker_action,
        )

    def _execute_order(
        self,
        *,
        client_id: str,
        ticker: str,
        size: int,
        price: float,
        action: OrderAction,
    ):
        # Executa a ordem para o cliente (se não for MARKET)
        if client_id != MarketLiquidity.MARKET_CLIENT_ID:
            match action:
                case OrderAction.BUY:
                    self._execute_buy(client_id, ticker, size, price)
                case OrderAction.SELL:
                    self._execute_sell(client_id, ticker, size, price)

    def _validate_order(
        self,
        *,
        client_id: str,
        ticker: str,
        qty: int,
        cost: float,
        action: OrderAction,
    ):
        """Valida se o cliente pode executar a ordem. Se o cliente for MARKET, faz bypass."""
        if client_id == MarketLiquidity.MARKET_CLIENT_ID:
            return

        if action == OrderAction.SELL and (
            ticker not in self._positions[client_id]
            or self._positions[client_id][ticker].size < qty
        ):
            raise InsufficentPositionError()

        if (
            action == OrderAction.BUY
            and self._simulation_engine.get_cash(client_id) < cost
        ):
            raise InsufficentCashError()

    def _execute_buy(self, client_id: str, ticker: str, size: int, price: float):
        cost = price * size

        self._simulation_engine.add_cash(client_id, -cost)

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
