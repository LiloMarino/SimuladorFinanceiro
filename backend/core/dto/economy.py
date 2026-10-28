from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO


class EconomyPointDTO(BaseDTO):
    """A economia num dia da partida; as taxas são frações (0.1425 = 14,25% ao ano)."""

    date: date
    selic: Decimal
    # Inflação acumulada em 12 meses
    ipca: Decimal
    # SELIC menos IPCA: quanto o dinheiro rende de verdade
    real_rate: Decimal
    # Meta de inflação do ano
    target: Decimal
    # Folga da meta: a inflação dentro de meta ± tolerância cumpre o regime de metas
    tolerance: Decimal


class CopomChangeDTO(BaseDTO):
    """Dia em que a SELIC mudou de nível."""

    date: date
    # A mudança em fração (0.005 = sobe 0,5 ponto)
    change: Decimal
    # A SELIC depois da mudança
    selic: Decimal


class EconomyPanelDTO(BaseDTO):
    points: list[EconomyPointDTO]
    copom_changes: list[CopomChangeDTO]
