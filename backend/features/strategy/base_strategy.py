from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.features.simulation.broker import Broker


class BaseStrategy:
    """Classe base para estratégias. Deve ser herdada por todas as estratégias."""

    def __init__(self, broker: Broker):
        self.broker = broker
        self.data_buffer = broker.data_buffer

    def next(self):
        """Executa a lógica da estratégia a cada tick."""
        raise NotImplementedError("Método next() deve ser implementado pela estratégia")
