from backend.core.dto.base import BaseDTO


class StockDTO(BaseDTO):
    id: int
    ticker: str
    name: str
