from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from backend.core import repository
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.position import PositionDTO
from backend.core.enum import EquityEventType
from backend.core.logger import setup_logger
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils.lazy_dict import LazyDict
from backend.features.realtime import notify
from backend.features.variable_income.entities.order import OrderAction
from backend.features.variable_income.entities.position import Position

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
    def __init__(
        self,
        simulation_engine: SimulationEngine,
    ):
        self._simulation_engine = simulation_engine
        self._positions: LazyDict[str, dict[str, Position]] = LazyDict(load_positions)

    def get_positions(self, client_id: str) -> dict[str, Position]:
        return self._positions[client_id]

    def execute_order(
        self,
        *,
        client_id: str,
        ticker: str,
        size: int,
        price: float,
        action: OrderAction,
    ):
        if size <= 0:
            raise ValueError("Quantidade deve ser maior que zero")

        match action:
            case OrderAction.BUY:
                self._execute_buy(client_id, ticker, size, price)
            case OrderAction.SELL:
                self._execute_sell(client_id, ticker, size, price)

    def _execute_buy(self, client_id: str, ticker: str, size: int, price: float):
        cost = price * size

        if self._simulation_engine.get_cash(client_id) < cost:
            raise ValueError("Saldo insuficiente")

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
            f"position_update:{ticker}",
            PositionDTO.from_model(self._positions[client_id][ticker]).to_json(),
            to=client_id,
        )
        logger.info(f"Executado BUY {size}x {ticker} @ R$ {price}")

    def _execute_sell(self, client_id: str, ticker: str, size: int, price: float):
        if ticker not in self._positions[client_id]:
            raise ValueError(f"Sem posição em {ticker}")

        pos = self._positions[client_id][ticker]
        if pos.size < size:
            raise ValueError("Quantidade insuficiente")

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
            f"position_update:{ticker}",
            PositionDTO.from_model(self._positions[client_id][ticker]).to_json(),
            to=client_id,
        )
        if pos.size == 0:
            del self._positions[client_id][ticker]

        logger.info(f"Executado SELL {size}x {ticker} @ R$ {price}")
