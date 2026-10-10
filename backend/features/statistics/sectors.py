"""Exposição, diversificação e lucro por setor, reconstruídos das execuções."""

from collections import defaultdict
from collections.abc import Mapping
from decimal import Decimal

from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.sector import SectorAllocationDTO, StockSegmentDTO
from backend.core.dto.statistics_report import SectorProfitDTO
from backend.core.enum import EquityEventType


def final_quantities(trades: list[EquityEventDTO]) -> dict[str, int]:
    """Quantidade em carteira de cada ativo depois de todas as execuções."""
    quantities: dict[str, int] = defaultdict(int)
    for trade in trades:
        sign = 1 if trade.event_type is EquityEventType.BUY else -1
        quantities[trade.ticker] += sign * trade.quantity
    return {ticker: q for ticker, q in quantities.items() if q > 0}


def position_values(
    trades: list[EquityEventDTO], prices: Mapping[str, Decimal]
) -> dict[str, Decimal]:
    return {
        ticker: quantity * prices.get(ticker, Decimal(0))
        for ticker, quantity in final_quantities(trades).items()
    }


def effective_sectors(sectors: list[SectorAllocationDTO]) -> Decimal | None:
    """
    Número efetivo de setores, 1 ÷ Σ fração²: tudo num setor vale 1, quatro
    setores iguais valem 4, e 70/10/10/10 vale ~1,9 (quase um setor só).
    """
    concentration = sum((s.fraction**2 for s in sectors), Decimal(0))
    return 1 / concentration if concentration else None


def sector_profit(
    trades: list[EquityEventDTO],
    prices: Mapping[str, Decimal],
    classification: Mapping[str, StockSegmentDTO],
) -> list[SectorProfitDTO]:
    """
    Resultado de cada setor: o que entrou nas vendas, menos o que saiu nas
    compras, mais o valor do que ainda está na carteira. Do maior lucro ao maior
    prejuízo.
    """
    by_ticker: dict[str, Decimal] = defaultdict(Decimal)
    for trade in trades:
        sign = -1 if trade.event_type is EquityEventType.BUY else 1
        by_ticker[trade.ticker] += sign * trade.quantity * trade.price
    for ticker, value in position_values(trades, prices).items():
        by_ticker[ticker] += value

    by_sector: dict[str | None, Decimal] = defaultdict(Decimal)
    for ticker, profit in by_ticker.items():
        segment = classification.get(ticker)
        by_sector[segment.sector if segment else None] += profit

    return sorted(
        (SectorProfitDTO(sector=s, profit=p) for s, p in by_sector.items()),
        key=lambda s: s.profit,
        reverse=True,
    )
