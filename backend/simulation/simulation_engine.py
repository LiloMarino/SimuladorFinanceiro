from backend.simulation.broker import Broker
from backend.simulation.data_buffer import DataBuffer
from backend.simulation.entities.candle import Candle


class SimulationEngine:
    def __init__(self):
        self._broker = Broker(self.get_market_price)
        self._data_buffer = DataBuffer()
        self._strategy = None

    def set_strategy(self, strategy_cls, *args, **kwargs):
        self._strategy = strategy_cls(self, *args, **kwargs)

    def get_broker(self) -> Broker:
        return self._broker

    def get_data_buffer(self) -> DataBuffer:
        return self._data_buffer

    def get_cash(self) -> float:
        return self._broker.get_cash()

    def get_positions(self):
        return self._broker.get_positions()

    def get_market_price(self, ticker: str) -> float:
        candles = self._data_buffer.get_recent(ticker)
        if not candles:
            raise ValueError(f"Nenhum preço disponível para {ticker}")
        return candles[-1].price

    def update_market_data(self, stocks: list[dict]):
        for s in stocks:
            candle = Candle(
                ticker=s["ticker"],
                date=s["date"],
                open=s["open"],
                high=s["high"],
                low=s["low"],
                close=s["price"],
                volume=s["volume"],
            )
            self._data_buffer.add_candle(candle)

    def next(self):
        if not self._strategy:
            raise RuntimeError("Nenhuma estratégia configurada")
        self._strategy.next()
