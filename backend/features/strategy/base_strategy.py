from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine


class BaseStrategy:
    """Classe base para estratégias. Deve ser herdada por todas as estratégias."""

    def __init__(self, engine: SimulationEngine):
        self.engine = engine
        self.broker = engine.broker
        self.data_buffer = engine.data_buffer

    def next(self):
        """Executa a lógica da estratégia a cada tick."""
        raise NotImplementedError("Método next() deve ser implementado pela estratégia")
