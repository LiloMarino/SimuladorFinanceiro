from __future__ import annotations

from backend.core.dto.base import BaseDTO
from backend.core.models.models import TickerProfile


class TickerProfileDTO(BaseDTO):
    ticker: str
    name: str | None
    quote_type: str | None
    sector: str | None
    industry: str | None

    @staticmethod
    def from_model(m: TickerProfile) -> TickerProfileDTO:
        return TickerProfileDTO(
            ticker=m.ticker,
            name=m.name,
            quote_type=m.quote_type,
            sector=m.sector,
            industry=m.industry,
        )


class TickerSuggestionDTO(BaseDTO):
    ticker: str
    name: str
