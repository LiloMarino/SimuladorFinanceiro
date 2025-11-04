from backend.realtime import notify
from backend.simulation.broker import Broker
from backend.simulation.data_buffer import DataBuffer
from backend.simulation.entities.candle import Candle
from backend.simulation.entities.portfolio import Portfolio
from backend.simulation.fixed_broker import FixedBroker


class SimulationEngine:
    def __init__(self, starting_cash: float = 10000.0):
        self._data_buffer = DataBuffer()
        self.__cash: float = starting_cash
        self._broker = Broker(self, self.get_market_price)
        self._fixed_broker = FixedBroker(self)
        self._strategy = None

    def set_strategy(self, strategy_cls, *args, **kwargs):
        self._strategy = strategy_cls(self, *args, **kwargs)

    def get_broker(self) -> Broker:
        return self._broker

    def get_fixed_broker(self) -> FixedBroker:
        return self._fixed_broker

    def get_data_buffer(self) -> DataBuffer:
        return self._data_buffer

    def get_cash(self) -> float:
        return self.__cash

    def add_cash(self, cash: float):
        self.__cash += cash
        notify("cash_update", {"cash": self.__cash})

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

    def get_portfolio(self) -> Portfolio:
        return Portfolio(
            cash=self.__cash,
            variable_income=list(self._broker.get_positions().values()),
            fixed_income=list(self._fixed_broker.get_assets().values()),
        )

    def next(self):
        # Aplica juros dos ativos de renda fixa
        self._fixed_broker.apply_daily_interest()

        # Executa a estratégia
        if not self._strategy:
            raise RuntimeError("Nenhuma estratégia configurada")
        self._strategy.next()
