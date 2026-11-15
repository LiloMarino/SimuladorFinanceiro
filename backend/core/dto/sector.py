from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.enum import StateLever


class StockSegmentDTO(BaseDTO):
    sector: str
    segment: str


class StockSuggestionDTO(StockSegmentDTO):
    """Sugestão da importação: setor e segmento, mais o que a marcação de estatal aproveita."""

    shares_outstanding: int | None = None
    lever: StateLever | None = None


class SectorDTO(BaseDTO):
    name: str
    segments: list[str]


class SegmentAllocationDTO(BaseDTO):
    segment: str | None
    value: Decimal
    fraction: Decimal


class SectorAllocationDTO(BaseDTO):
    # None agrupa as ações ainda sem classificação ("Sem setor")
    sector: str | None
    value: Decimal
    # Frações (0.25 = 25%) sobre o valor total agrupado; a do segmento também
    fraction: Decimal
    segments: list[SegmentAllocationDTO]
