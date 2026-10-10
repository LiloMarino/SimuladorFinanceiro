"""Agrupamento de valores por setor e segmento, a partir da classificação das ações."""

from collections import defaultdict
from collections.abc import Mapping
from decimal import Decimal

from backend.core.dto.sector import (
    SectorAllocationDTO,
    SegmentAllocationDTO,
    StockSegmentDTO,
)
from backend.core.utils import ratio


def allocate_by_sector(
    values: Mapping[str, Decimal], classification: Mapping[str, StockSegmentDTO]
) -> list[SectorAllocationDTO]:
    """
    Soma o valor de cada ticker no seu setor e segmento, do maior setor para o
    menor; ticker sem classificação cai no grupo None.
    """
    by_sector: dict[str | None, dict[str | None, Decimal]] = defaultdict(
        lambda: defaultdict(Decimal)
    )
    for ticker, value in values.items():
        segment = classification.get(ticker)
        if segment:
            by_sector[segment.sector][segment.segment] += value
        else:
            by_sector[None][None] += value

    total = sum(values.values(), Decimal(0))
    sectors = [
        SectorAllocationDTO(
            sector=sector,
            value=sum(segments.values(), Decimal(0)),
            fraction=ratio(sum(segments.values(), Decimal(0)), total),
            segments=sorted(
                (
                    SegmentAllocationDTO(
                        segment=name, value=value, fraction=ratio(value, total)
                    )
                    for name, value in segments.items()
                ),
                key=lambda s: s.value,
                reverse=True,
            ),
        )
        for sector, segments in by_sector.items()
    ]
    return sorted(sectors, key=lambda s: s.value, reverse=True)
