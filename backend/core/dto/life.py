from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.enum import LifeEventEffect, LifeHistoryCategory, LifeHistoryKind


class LifeEventDTO(BaseDTO):
    """Imprevisto sorteado no pregão: o mesmo para todos os jogadores."""

    key: str
    label: str
    effect: LifeEventEffect
    # Quanto saiu do caixa de cada jogador; zero na demissão, que tira o salário do mês seguinte
    amount: Decimal
    event_date: date


class LifeStatusDTO(BaseDTO):
    """A vida financeira de quem pede, no pregão corrente do viver de renda."""

    monthly_salary: Decimal
    monthly_expense: Decimal
    # Pregão da demissão do mês anterior: o salário deste mês não entrou
    salary_skipped_by: date | None
    # Pregão da demissão deste mês: o salário do próximo não entra
    next_salary_skipped_by: date | None
    goal: Decimal
    inflation_adjusted: bool
    withdrawal_rate: Decimal
    unexpected_per_year: int
    overdraft_monthly_rate: Decimal
    # Juro que o caixa de hoje paga por pregão; zero com caixa positivo
    overdraft_daily_interest: Decimal
    # Quantos meses de despesa o caixa cobre; zero com caixa negativo
    reserve_months: Decimal


class LifeHistoryRowDTO(BaseDTO):
    event_date: date
    category: LifeHistoryCategory
    kind: LifeHistoryKind
    # Chave e rótulo do imprevisto; nulos nas linhas do cheque especial
    life_event_key: str | None = None
    label: str | None = None
    # Efeito no caixa (negativo quando saiu); nulo quando o evento não moveu dinheiro
    amount: Decimal | None = None
    cash_after: Decimal


class LifeHistoryCountsDTO(BaseDTO):
    all: int
    unexpected: int
    layoff: int
    overdraft: int


class LifeHistoryPageDTO(BaseDTO):
    # Na ordenação pedida; o padrão é do mais recente ao mais antigo.
    items: list[LifeHistoryRowDTO]
    # Linhas da categoria pedida, para o "Mostrar mais"
    total: int
    counts: LifeHistoryCountsDTO
