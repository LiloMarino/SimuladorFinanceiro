from datetime import date

from pydantic import BaseModel


class StockStatusDTO(BaseModel):
    ticker: str
    last_date: date | None
