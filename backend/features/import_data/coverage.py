from collections import defaultdict

from backend.core import repository
from backend.core.dto.sector import StockSegmentDTO
from backend.core.dto.series_coverage import (
    OriginCoverageDTO,
    SeriesCoverageDTO,
    SeriesKind,
)
from backend.core.enum import AssetClass, DataOrigin
from backend.features.import_data.indicators import INDICATOR_SOURCES


def get_series_coverage() -> list[SeriesCoverageDTO]:
    """Toda série da base, indicadores primeiro, com o trecho real e o gerado."""
    indicators = _by_key(repository.economic.get_coverage())
    stocks = _by_key(repository.stock.get_coverage())
    classification = repository.stock.get_classification()

    return [
        _series(SeriesKind.INDICATOR, series.value, source.name, indicators)
        for series, source in INDICATOR_SOURCES.items()
    ] + [
        _series(
            SeriesKind.STOCK,
            stock.ticker,
            stock.name,
            stocks,
            stock.asset_class,
            classification.get(stock.ticker),
        )
        for stock in repository.stock.get_stocks()
    ]


def _by_key(
    rows: list[OriginCoverageDTO],
) -> dict[str, dict[DataOrigin, OriginCoverageDTO]]:
    grouped: dict[str, dict[DataOrigin, OriginCoverageDTO]] = defaultdict(dict)
    for row in rows:
        grouped[row.key][row.origin] = row
    return grouped


def _series(
    kind: SeriesKind,
    key: str,
    name: str,
    coverage: dict[str, dict[DataOrigin, OriginCoverageDTO]],
    asset_class: AssetClass | None = None,
    segment: StockSegmentDTO | None = None,
) -> SeriesCoverageDTO:
    origins = coverage.get(key, {})
    real = origins.get(DataOrigin.REAL)
    generated = origins.get(DataOrigin.GENERATED)
    starts = [c.start for c in origins.values()]
    return SeriesCoverageDTO(
        kind=kind,
        key=key,
        name=name,
        start=min(starts) if starts else None,
        real_end=real.end if real else None,
        generated_end=generated.end if generated else None,
        asset_class=asset_class,
        segment=segment,
    )
