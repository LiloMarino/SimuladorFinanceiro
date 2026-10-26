from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from backend.core.dto.base import BaseDTO


class PositionResultDTO(BaseDTO):
    """O que uma posição de renda variável rendeu no período, em reais e sobre o capital dela."""

    ticker: str
    name: str
    result: Decimal
    # Sobre o valor da posição no início mais o que se comprou no período; nulo sem capital
    result_pct: Decimal | None


class RankingMoveDTO(BaseDTO):
    position: int
    players: int
    # Quantas posições subiu (positivo) ou desceu (negativo) desde o resumo anterior; nulo no primeiro
    change: int | None


class MonthSummaryDTO(BaseDTO):
    kind: Literal["MONTH_SUMMARY"] = "MONTH_SUMMARY"
    # Primeiro dia do mês resumido
    month: date
    networth_start: Decimal
    networth_end: Decimal
    # Rentabilidade da cota no mês, que os aportes não movem; nula sem pregão com patrimônio positivo
    return_pct: Decimal | None
    cdi_pct: Decimal
    # Nula sem a série do Ibovespa no período
    ibov_pct: Decimal | None
    best_position: PositionResultDTO | None
    worst_position: PositionResultDTO | None
    dividends: Decimal
    income_tax: Decimal
    # Aportes no viver de renda: salário menos despesa e imprevistos
    contributions: Decimal
    ranking: RankingMoveDTO | None


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


InboxContent = Annotated[MonthSummaryDTO | YearReviewDTO, Field(discriminator="kind")]


class InboxEntryDTO(BaseDTO):
    id: int
    game_date: date
    # Da sala inteira, e não só de quem lê
    room: bool
    read: bool
    content: InboxContent


class InboxDTO(BaseDTO):
    # Da mais nova para a mais antiga
    entries: list[InboxEntryDTO]
    unread: int
