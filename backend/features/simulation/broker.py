from __future__ import annotations

from typing import TYPE_CHECKING

from backend.core.logger import setup_logger
from backend.features.simulation.data_buffer import DataBuffer
from backend.features.simulation.entities.position import Position

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine

logger = setup_logger(__name__)


class Broker:
    def __init__(
        self,
        simulation_engine: SimulationEngine,
    ):
        self.data_buffer = DataBuffer()
        self._simulation_engine = simulation_engine
        self._positions: dict[str, Position] = {}

    def get_positions(self) -> dict[str, Position]:
        return self._positions

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
        if ticker not in self._positions:
            self._positions[ticker] = Position(ticker)
        self._positions[ticker].update_buy(price, size)
        logger.info(
            f"Executado compra {size}x {ticker} (a mercado) no preço R$ {price}"
        )

    def sell(self, client_id: str, ticker: str, size: int):
        if size <= 0:
            raise ValueError("Quantidade para venda deve ser maior que zero")

        if ticker not in self._positions:
            raise ValueError(f"Sem posição em {ticker} para vender")

        pos = self._positions[ticker]
        if pos.size < size:
            raise ValueError(f"Sem quantidade suficiente de {ticker} para vender")

        price = self.get_market_price(ticker)
        self._simulation_engine.add_cash(client_id, price * size)
        pos.update_sell(size)

        if pos.size == 0:
            del self._positions[ticker]
        logger.info(f"Executado venda {size}x {ticker} (a mercado) no preço R$ {price}")
