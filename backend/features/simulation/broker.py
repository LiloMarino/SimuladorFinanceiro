from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from backend.core import repository
from backend.core.dto.events.equity import EquityEventDTO, EquityEventType
from backend.core.logger import setup_logger
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils.lazy_dict import LazyDict
from backend.features.simulation.data_buffer import DataBuffer
from backend.features.simulation.entities.position import Position

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
        )

    return positions


class Broker:
    def __init__(
        self,
        simulation_engine: SimulationEngine,
    ):
        self.data_buffer = DataBuffer()
        self._simulation_engine = simulation_engine
        self._positions: LazyDict[str, dict[str, Position]] = LazyDict(load_positions)

    def get_positions(self, client_id: str) -> dict[str, Position]:
        return self._positions[client_id]

    def get_market_price(self, ticker: str) -> float:
        candles = self.data_buffer.get_recent(ticker)
        if not candles:
            raise ValueError(f"Nenhum preço disponível para {ticker}")
        return candles[-1].price

    def buy(self, client_id: str, ticker: str, size: int):
        if size <= 0:
            raise ValueError("Quantidade para compra deve ser maior que zero")
        price = self.get_market_price(ticker)
        cost = price * size
        if self._simulation_engine.get_cash(client_id) < cost:
            raise ValueError(f"Saldo insuficiente para comprar {ticker}")

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
                event_date=self._simulation_engine.current_date.date(),
            )
        )
        logger.info(
            f"Executado compra {size}x {ticker} (a mercado) no preço R$ {price}"
        )

    def sell(self, client_id: str, ticker: str, size: int):
        if size <= 0:
            raise ValueError("Quantidade para venda deve ser maior que zero")

        if ticker not in self._positions[client_id]:
            raise ValueError(f"Sem posição em {ticker} para vender")

        pos = self._positions[client_id][ticker]
        if pos.size < size:
            raise ValueError(f"Sem quantidade suficiente de {ticker} para vender")

        price = self.get_market_price(ticker)
        self._simulation_engine.add_cash(client_id, price * size)
        pos.update_sell(size)
        EventManager.push_event(
            EquityEventDTO(
                user_id=UserManager.get_user_id(client_id),
                event_type=EquityEventType.SELL,
                ticker=ticker,
                quantity=size,
                price=Decimal(price),
                event_date=self._simulation_engine.current_date.date(),
            )
        )
        if pos.size == 0:
            del self._positions[client_id][ticker]
        logger.info(f"Executado venda {size}x {ticker} (a mercado) no preço R$ {price}")
