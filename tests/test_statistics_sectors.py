"""Exposição, diversificação e lucro por setor reconstruídos das execuções."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.sector import SectorAllocationDTO, StockSegmentDTO
from backend.core.enum import EquityEventType
from backend.features.statistics import sectors

DAY = date(2020, 1, 6)
BUY, SELL = EquityEventType.BUY, EquityEventType.SELL
CLASSIFICATION = {
    "ITUB4": StockSegmentDTO(sector="Financeiro", segment="Bancos"),
    "VALE3": StockSegmentDTO(sector="Materiais Básicos", segment="Mineração"),
}


def trade(ticker: str, kind: EquityEventType, quantity: int, price: str):
    return EquityEventDTO(
        simulation_id=1,
        user_id=1,
        event_date=DAY,
        ticker=ticker,
        event_type=kind,
        quantity=quantity,
        price=Decimal(price),
    )


def allocation(*fractions: str) -> list[SectorAllocationDTO]:
    return [
        SectorAllocationDTO(
            sector=str(i), value=Decimal(f), fraction=Decimal(f), segments=[]
        )
        for i, f in enumerate(fractions)
    ]


def test_effective_sectors():
    """Um setor vale 1; quatro iguais valem 4; 70/10/10/10 vale ~1,92."""
    assert sectors.effective_sectors(allocation("1")) == 1
    assert sectors.effective_sectors(allocation("0.25", "0.25", "0.25", "0.25")) == 4
    concentrated = sectors.effective_sectors(allocation("0.7", "0.1", "0.1", "0.1"))
    assert concentrated is not None
    assert float(concentrated) == pytest.approx(1.923, abs=1e-3)
    assert sectors.effective_sectors([]) is None


def test_final_positions_and_values():
    """Comprou 100 e vendeu 40 de ITUB4; vendeu tudo de VALE3."""
    trades = [
        trade("ITUB4", BUY, 100, "30"),
        trade("ITUB4", SELL, 40, "32"),
        trade("VALE3", BUY, 10, "60"),
        trade("VALE3", SELL, 10, "55"),
    ]
    assert sectors.position_values(trades, {"ITUB4": Decimal("35")}) == {
        "ITUB4": Decimal("2100")
    }


def test_sector_profit_counts_open_positions_at_last_price():
    """
    ITUB4: -3.000 na compra, +1.280 na venda, 60 x R$ 35 = R$ 2.100 em carteira
    → +R$ 380. VALE3: -600 + 550 → -R$ 50. XPTO3 sem setor: -100 + 120 → +R$ 20.
    """
    trades = [
        trade("ITUB4", BUY, 100, "30"),
        trade("ITUB4", SELL, 40, "32"),
        trade("VALE3", BUY, 10, "60"),
        trade("VALE3", SELL, 10, "55"),
        trade("XPTO3", BUY, 10, "10"),
        trade("XPTO3", SELL, 10, "12"),
    ]
    profit = sectors.sector_profit(trades, {"ITUB4": Decimal("35")}, CLASSIFICATION)

    assert [(p.sector, p.profit) for p in profit] == [
        ("Financeiro", Decimal("380")),
        (None, Decimal("20")),
        ("Materiais Básicos", Decimal("-50")),
    ]
