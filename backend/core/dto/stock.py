from dataclasses import dataclass

from backend.core.dto.base import BaseDTO


@dataclass(frozen=True, kw_only=True)
class StockDTO(BaseDTO):
    id: int
    ticker: str
    name: str
