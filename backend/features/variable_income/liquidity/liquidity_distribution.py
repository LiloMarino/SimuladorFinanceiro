from abc import ABC, abstractmethod
from dataclasses import dataclass

from backend.features.variable_income.entities.candle import Candle


@dataclass(slots=True, frozen=True, kw_only=True)
class PriceLevel:
    price: float
    volume: int


class LiquidityDistribution(ABC):
    """
    Contrato para geradores de liquidez sintética baseados em OHLCV.

    Responsabilidade:
    - Traduzir um Candle em níveis de liquidez (preço + volume)

    Garantias esperadas:
    - Nenhum PriceLevel com level.price fora do range do [low, high]
    - sum(level.volume) == candle.volume
    """

    @abstractmethod
    def generate(self, candle: Candle) -> list[PriceLevel]:
        """
        Traduz um Candle (OHLCV) em níveis de liquidez (preço, volume).

        Implementações DEVEM:
        - Ser determinísticas para o mesmo candle
        - Não mutar o candle
        - Retornar lista vazia se não houver liquidez válida.
        """
        raise NotImplementedError
