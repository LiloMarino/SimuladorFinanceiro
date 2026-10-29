from datetime import date

from backend.core.dto.base import BaseDTO
from backend.core.enum import NewsType


class NewsDTO(BaseDTO):
    """Uma manchete do jornal da partida; a seção e o nível vêm do tipo, no registro."""

    id: int
    news_date: date
    news_type: NewsType
    headline: str
    # A linha de apoio abaixo da manchete
    dek: str | None
    tickers: list[str]
