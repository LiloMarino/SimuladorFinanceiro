from datetime import date
from enum import Enum

from backend.core.dto.base import BaseDTO
from backend.core.enum import DataOrigin


class SeriesKind(Enum):
    STOCK = "STOCK"
    INDICATOR = "INDICATOR"


class OriginCoverageDTO(BaseDTO):
    """Primeiro e último dia de uma série numa origem."""

    key: str
    origin: DataOrigin
    start: date
    end: date


class SeriesCoverageDTO(BaseDTO):
    kind: SeriesKind
    key: str
    name: str
    start: date | None
    real_end: date | None
    generated_end: date | None
