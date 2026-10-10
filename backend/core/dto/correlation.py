"""
Correlação entre os retornos diários de ativos, par a par. A matriz vem
completa e simétrica, com o IBOV como última linha e coluna.
"""

from datetime import date
from decimal import Decimal
from typing import Literal

from backend.core.dto.base import BaseDTO

type CorrelationWindow = Literal["6m", "1y", "3y", "5y"]


class CorrelationCellDTO(BaseDTO):
    # De -1 a 1; None quando os pregões em comum não chegam ao mínimo ou um
    # dos lados ficou parado na janela
    correlation: Decimal | None
    # Pregões em comum com retorno nos dois lados
    days: int


class CorrelationMatrixDTO(BaseDTO):
    labels: list[str]
    rows: list[list[CorrelationCellDTO]]
    start: date
    end: date
    min_days: int


class CorrelationAssetsDTO(BaseDTO):
    tickers: list[str]
    # Último dia que a janela pode alcançar; None sem nenhum preço no banco
    last_date: date | None
    # Na partida, a janela termina na data da simulação
    end_fixed: bool
