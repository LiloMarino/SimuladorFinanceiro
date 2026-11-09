from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, Field

from backend.core.dto.base import BaseDTO
from backend.core.enum import (
    IncomeLoss,
    LifeEventEffect,
    LifeHistoryCategory,
    LifeHistoryKind,
    Profession,
)
from backend.core.professions import TaxBase

LIFE_EVENT_LABEL_MAX_LENGTH = 40
LIFE_EVENT_MAX_EXPENSE_MULTIPLE = 24
LIFE_EVENTS_MAX_COUNT = 12


class LifeEventTypeDTO(BaseDTO):
    """Um tipo de imprevisto das regras da partida: o motor, o histórico e a tela leem a mesma lista."""

    key: str = Field(min_length=1, max_length=40)
    label: str = Field(min_length=1, max_length=LIFE_EVENT_LABEL_MAX_LENGTH)
    effect: LifeEventEffect
    # Chance relativa entre os tipos quando sai um imprevisto
    weight: int = Field(ge=1)
    # Quantas despesas mensais saem do caixa; a demissão não usa
    expense_multiple: Decimal = Field(ge=0, le=LIFE_EVENT_MAX_EXPENSE_MULTIPLE)
    enabled: bool


DEFAULT_LIFE_EVENTS: tuple[LifeEventTypeDTO, ...] = (
    LifeEventTypeDTO(
        key="REPAIR",
        label="Conserto do carro",
        effect=LifeEventEffect.CASH_OUT,
        weight=3,
        expense_multiple=Decimal(1),
        enabled=True,
    ),
    LifeEventTypeDTO(
        key="HEALTH",
        label="Despesa de saúde",
        effect=LifeEventEffect.CASH_OUT,
        weight=2,
        expense_multiple=Decimal(2),
        enabled=True,
    ),
    LifeEventTypeDTO(
        key="LAYOFF",
        label="Demissão",
        effect=LifeEventEffect.SKIP_NEXT_SALARY,
        weight=1,
        expense_multiple=Decimal(0),
        enabled=True,
    ),
)


def validate_life_events(
    events: list[LifeEventTypeDTO],
) -> list[LifeEventTypeDTO]:
    """Os tipos de fábrica ficam sempre na lista (só se desligam) e as chaves não se repetem."""
    keys = [event.key for event in events]
    if len(set(keys)) != len(keys):
        raise ValueError("Cada tipo de imprevisto precisa de uma chave única.")
    if len(events) > LIFE_EVENTS_MAX_COUNT:
        raise ValueError(
            f"No máximo {LIFE_EVENTS_MAX_COUNT} tipos de imprevisto por partida."
        )
    for default in DEFAULT_LIFE_EVENTS:
        found = next((e for e in events if e.key == default.key), None)
        if found is None:
            raise ValueError(f"O tipo «{default.label}» não pode ser removido.")
        if found.effect is not default.effect:
            raise ValueError(f"O efeito do tipo «{default.label}» não muda.")
    return events


# A lista de tipos das regras da partida; o padrão é o catálogo de fábrica
LifeEventTypes = Annotated[list[LifeEventTypeDTO], AfterValidator(validate_life_events)]


def default_life_events() -> list[LifeEventTypeDTO]:
    return list(DEFAULT_LIFE_EVENTS)


class LifeEventDTO(BaseDTO):
    """Imprevisto sorteado no pregão: o mesmo para todos os jogadores, que cada um sente pela profissão."""

    key: str
    label: str
    effect: LifeEventEffect
    # Quanto saiu do caixa de cada jogador; zero na demissão, que tira o salário do mês seguinte
    amount: Decimal
    event_date: date
    # O que a demissão sorteada é para quem recebe o aviso (demissão, queda do bico ou vacância)
    income_loss: IncomeLoss | None = None


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
    # A cobertura automática também vende Prefixado e IPCA+ (a mercado); os títulos sem perda sempre entram
    cover_with_treasury: bool
    # Só no viver de renda com profissões: a do jogador e o que a atinge no dia
    profession: Profession | None = None
    # O que o sorteio da demissão é para a profissão; nulo quando ela o ignora
    income_loss: IncomeLoss | None = None
    # Quantas vezes o imprevisto de saúde pesa para a profissão
    health_multiple: Decimal = Decimal(1)
    # O imposto que mexe na renda da profissão, a alíquota em vigor e a da lei
    tax: TaxBase | None = None
    tax_rate: Decimal | None = None
    tax_reference: Decimal | None = None
    # O reajuste real em vigor (servidores ou aposentados); nulo nas outras profissões
    real_raise: Decimal | None = None
    # O gasto com auxílio em fração do PIB; nulo fora da profissão que o recebe
    welfare_spending: Decimal | None = None
    # O PIB de 12 meses que move a renda do empreendedor; nulo nas outras profissões
    gdp_growth: Decimal | None = None


class LifeHistoryRowDTO(BaseDTO):
    event_date: date
    category: LifeHistoryCategory
    kind: LifeHistoryKind
    # Chave e rótulo do imprevisto; nulos nas linhas do cheque especial. Nas linhas de
    # orçamento e na demissão, o rótulo traz o valor novo e a origem na economia
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
    budget: int


class LifeHistoryPageDTO(BaseDTO):
    # Na ordenação pedida; o padrão é do mais recente ao mais antigo.
    items: list[LifeHistoryRowDTO]
    # Linhas da categoria pedida, para o "Mostrar mais"
    total: int
    counts: LifeHistoryCountsDTO
    # Juro do cheque especial pago na partida inteira (positivo), qualquer que seja o filtro
    interest_paid: Decimal
