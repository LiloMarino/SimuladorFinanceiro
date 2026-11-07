from __future__ import annotations

from datetime import date

from backend.core.dto.base import BaseDTO
from backend.core.enum import CorporateEventKind
from backend.core.models.models import StockCorporateEvent


class CorporateEventDTO(BaseDTO):
    stock_id: int
    ex_date: date
    kind: CorporateEventKind
    # SPLIT: razão (2 é 2:1; 0,1 é grupamento 10:1). DIVIDEND: valor bruto por cota
    value: float

    @staticmethod
    def from_model(m: StockCorporateEvent) -> CorporateEventDTO:
        return CorporateEventDTO(
            stock_id=m.stock_id,
            ex_date=m.ex_date,
            kind=CorporateEventKind(m.kind),
            value=float(m.value),
        )
