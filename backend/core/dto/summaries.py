from datetime import date
from decimal import Decimal
from typing import Literal

from backend.core.dto.base import BaseDTO


class YearMonthDTO(BaseDTO):
    month: date
    return_pct: Decimal
    networth_end: Decimal


class YearReviewDTO(BaseDTO):
    kind: Literal["YEAR_REVIEW"] = "YEAR_REVIEW"
    year: int
    networth_start: Decimal
    networth_end: Decimal
    return_pct: Decimal | None
    cdi_pct: Decimal
    ibov_pct: Decimal | None
    contributions: Decimal
    # Os meses jogados no ano, em ordem
    months: list[YearMonthDTO]
    best_month: YearMonthDTO | None
    worst_month: YearMonthDTO | None


class SummaryDTO(BaseDTO):
    """Uma retrospectiva entregue a um jogador na virada do ano."""

    id: int
    game_date: date
    content: YearReviewDTO
