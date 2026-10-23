from datetime import date
from decimal import Decimal
from uuid import UUID

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


class OverdraftCoverDTO(BaseDTO):
    """O título de liquidez diária que sozinho paga o cheque especial hoje."""

    asset_uuid: UUID
    asset_name: str
    # O que cai no caixa: a dívida inteira
    net_amount: Decimal
    # O que sai do título para render esse líquido, com os impostos
    gross_amount: Decimal


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
    # Quantos meses de despesa a reserva (caixa mais liquidez diária) cobre; zero se a soma é negativa
    reserve_months: Decimal
    # As duas partes da reserva, em reais: o caixa positivo e a liquidez diária líquida
    reserve_cash: Decimal
    reserve_daily_liquidity: Decimal
    # Com o caixa negativo, o título de menor taxa que cobre a dívida; None se nenhum cobre
    overdraft_cover: OverdraftCoverDTO | None


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
