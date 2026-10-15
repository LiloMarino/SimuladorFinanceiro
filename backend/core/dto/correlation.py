"""
Correlação entre os retornos diários de ativos, par a par. A matriz vem
completa e simétrica, com o IBOV como última linha e coluna.
"""

from datetime import date
from decimal import Decimal
from typing import Literal

from backend.core.dto.base import BaseDTO

type CorrelationWindow = Literal["6m", "1y", "3y", "5y"]

# Por que um par fica sem correlação: poucos pregões em comum, ou um lado parado
type CorrelationGap = Literal["insufficient_days", "constant_series"]


class CorrelationCellDTO(BaseDTO):
    # De -1 a 1; None junto com `reason`
    correlation: Decimal | None
    # Pregões em comum com retorno nos dois lados
    days: int
    reason: CorrelationGap | None = None


class CorrelationPairDTO(BaseDTO):
    first: str
    second: str
    correlation: Decimal


class PortfolioCorrelationDTO(BaseDTO):
    # As ações da carteira que estão na matriz
    tickers: list[str]
    # Média das correlações entre elas, par a par
    average: Decimal


class CorrelationHighlightsDTO(BaseDTO):
    # Entre os ativos escolhidos, sem o Ibovespa: o par que mais anda junto e o
    # de menor correlação, o melhor para diversificar
    most_similar: CorrelationPairDTO | None
    best_diversifier: CorrelationPairDTO | None
    # Com duas ou mais ações da carteira escolhidas
    portfolio: PortfolioCorrelationDTO | None


class CorrelationMatrixDTO(BaseDTO):
    labels: list[str]
    rows: list[list[CorrelationCellDTO]]
    start: date
    end: date
    min_days: int
    highlights: CorrelationHighlightsDTO


class CorrelationAssetDTO(BaseDTO):
    ticker: str
    sector: str | None


class CorrelationAssetsDTO(BaseDTO):
    assets: list[CorrelationAssetDTO]
    # Último dia que a janela pode alcançar; None sem nenhum preço no banco
    last_date: date | None
    # Na partida, a janela termina na data da simulação
    end_fixed: bool
