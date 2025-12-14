from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from backend.core.logger import setup_logger
from backend.features.simulation.entities.position import Position

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine

logger = setup_logger(__name__)


class Broker:
    def __init__(
        self,
        simulation_engine: SimulationEngine,
        get_market_price: Callable[[str], float],
    ):
        self._simulation_engine = simulation_engine
        self._positions: dict[str, Position] = {}
        self._get_market_price = get_market_price

    def get_positions(self) -> dict[str, Position]:
        return self._positions

    def buy(self, client_id: str, ticker: str, size: int):
        if size <= 0:
            raise ValueError("Quantidade para compra deve ser maior que zero")
        price = self._get_market_price(ticker)
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

        price = self._get_market_price(ticker)
        self._simulation_engine.add_cash(client_id, price * size)
        pos.update_sell(size)

        if pos.size == 0:
            del self._positions[ticker]
        logger.info(f"Executado venda {size}x {ticker} (a mercado) no preço R$ {price}")
