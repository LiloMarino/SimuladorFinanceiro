from datetime import date
from enum import Enum

from backend.core.dto.base import BaseDTO
from backend.core.dto.sector import StockSegmentDTO
from backend.core.enum import AssetClass, AssetOrigin, DataOrigin


class SeriesKind(Enum):
    STOCK = "STOCK"
    # Indicadores do mercado: limitam o período da partida
    INDICATOR = "INDICATOR"
    # Séries da economia do país (PIB, desemprego e dólar): não limitam a partida
    MACRO = "MACRO"


class OriginCoverageDTO(BaseDTO):
    """Primeiro e último dia de uma série numa origem."""

    key: str
    origin: DataOrigin
    start: date
    end: date
    # Pregões reais em que a fonte errou o preço e o fechamento é interpolado
    corrected_days: int = 0


class SeriesCoverageDTO(BaseDTO):
    kind: SeriesKind
    key: str
    name: str
    start: date | None
    real_end: date | None
    generated_end: date | None
    corrected_days: int
    # Só as ações têm classe; ela decide a alíquota do IR na venda
    asset_class: AssetClass | None
    # Só as ações têm origem; ela decide se o preço anda com o dólar da partida
    origin: AssetOrigin | None
    segment: StockSegmentDTO | None
