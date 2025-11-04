from dataclasses import dataclass
from typing import Callable, Dict

from backend import logger_utils

logger = logger_utils.setup_logger(__name__)


@dataclass
class Position:
    """Representa uma posição aberta em um ativo."""

    ticker: str
    size: int = 0
    avg_price: float = 0.0

    def update_buy(self, price: float, size: int):
        """Atualiza posição após uma compra."""
        if self.size + size == 0:
            self.avg_price = price
        else:
            total_cost = self.avg_price * self.size + price * size
            self.size += size
            self.avg_price = total_cost / self.size

    def update_sell(self, size: int):
        """Atualiza posição após uma venda."""
        self.size -= size
        if self.size < 0:
            raise ValueError("Venda excede posição disponível.")


class Broker:
    def __init__(
        self, get_market_price: Callable[[str], float], starting_cash: float = 10000.0
    ):
        self._cash: float = starting_cash
        self._positions: Dict[str, Position] = {}
        self._get_market_price = get_market_price

    def get_cash(self) -> float:
        return self._cash

    def set_cash(self, cash: float):
        self._cash = cash

    def get_positions(self) -> Dict[str, Position]:
        return self._positions

    def buy(self, ticker: str, size: int):
        price = self._get_market_price(ticker)
        cost = price * size
        if self._cash < cost:
            raise ValueError(f"Saldo insuficiente para comprar {ticker}")

        self._cash -= cost
        pos = self._positions.get(ticker, Position(ticker))
        pos.update_buy(price, size)
        self._positions[ticker] = pos
        logger.info(
            f"Executado compra {size}x {ticker} (a mercado) no preço R$ {price}"
        )

    def sell(self, ticker: str, size: int):
        if ticker not in self._positions:
            raise ValueError(f"Sem posição em {ticker} para vender")

        pos = self._positions[ticker]
        if pos.size < size:
            raise ValueError(f"Sem quantidade suficiente de {ticker} para vender")

        price = self._get_market_price(ticker)
        self._cash += price * size
        pos.update_sell(size)

        if pos.size == 0:
            del self._positions[ticker]
        else:
            self._positions[ticker] = pos
        logger.info(f"Executado venda {size}x {ticker} (a mercado) no preço R$ {price}")
