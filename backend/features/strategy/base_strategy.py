from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.features.variable_income.matching_engine import MatchingEngine


class BaseStrategy:
    """
    Classe base abstrata para estratégias de trading.

    Responsável por:
    - Definir interface comum para todas as estratégias (método next)
    - Fornecer acesso ao MatchingEngine para submissão de ordens
    - Fornecer acesso ao MarketData para análise de candles
    """

    def __init__(self, matching_engine: MatchingEngine):
        self.matching_engine = matching_engine
        self.market_data = matching_engine.market_data

    def next(self):
        """Executa a lógica da estratégia a cada tick."""
        raise NotImplementedError("Método next() deve ser implementado pela estratégia")
