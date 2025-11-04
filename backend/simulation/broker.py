from typing import Callable, Dict

from backend import logger_utils
from backend.realtime import notify
from backend.simulation.entities.position import Position

logger = logger_utils.setup_logger(__name__)


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

    def add_cash(self, cash: float):
        self._cash += cash
        notify("cash_update", {"cash": self._cash})

    def get_positions(self) -> Dict[str, Position]:
        return self._positions

    def buy(self, ticker: str, size: int):
        price = self._get_market_price(ticker)
        cost = price * size
        if self._cash < cost:
            raise ValueError(f"Saldo insuficiente para comprar {ticker}")

        self.add_cash(-cost)
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
        self.add_cash(price * size)
        pos.update_sell(size)

        if pos.size == 0:
            del self._positions[ticker]
        else:
            self._positions[ticker] = pos
        logger.info(f"Executado venda {size}x {ticker} (a mercado) no preço R$ {price}")
