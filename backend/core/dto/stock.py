from __future__ import annotations

from backend.core.dto.base import BaseDTO
from backend.core.enum import AssetClass
from backend.core.models.models import Stock


class StockDTO(BaseDTO):
    id: int
    ticker: str
    name: str
    asset_class: AssetClass

    @staticmethod
    def from_model(m: Stock) -> StockDTO:
        return StockDTO(
            id=m.id,
            ticker=m.ticker,
            name=m.name,
            asset_class=AssetClass(m.asset_class),
        )
