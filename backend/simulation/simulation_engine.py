from backend.simulation.broker import Broker
from backend.simulation.data_buffer import DataBuffer


class SimulationEngine:
    def __init__(self):
        self._broker = Broker()
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

    def next(self):
        """Executa um passo da simulação (tick)."""
        if not self._strategy:
            raise RuntimeError("Nenhuma estratégia configurada")
        self._strategy.next()
