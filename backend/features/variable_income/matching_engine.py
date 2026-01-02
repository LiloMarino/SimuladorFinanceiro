from backend.features.variable_income.broker import Broker
from backend.features.variable_income.entities.order import Order
from backend.features.variable_income.market_data import MarketData
from backend.features.variable_income.order_book import OrderBook


class MatchingEngine:
    def __init__(self, broker: Broker, market_data: MarketData):
        self.broker = broker
        self.market_data = market_data
        self.order_book = OrderBook()

    def submit(self, order: Order) -> None:
        """Recebe uma nova ordem (market ou limit)."""

    def on_tick(self, ticker: str) -> None:
        """Chamado a cada novo candle para processar ordens pendentes."""
