from datetime import date
from decimal import Decimal
from typing import Annotated, Any

from pydantic import AfterValidator, Field, model_validator

from backend.core.dto.base import BaseDTO
from backend.core.enum import (
    IncomeLoss,
    LifeEventEffect,
    LifeEventFamily,
    LifeFrequency,
    LifeHistoryCategory,
    LifeHistoryKind,
    Profession,
)
from backend.core.life_events import LIFE_EVENT_CATALOG
from backend.core.professions import IncomeDriver, TaxBase

LIFE_EVENT_LABEL_MAX_LENGTH = 40
LIFE_EVENT_MAX_EXPENSE_MULTIPLE = 24
LIFE_EVENTS_MAX_COUNT = 40

# A família de uma lista guardada antes de existirem famílias vem do efeito do tipo
_FAMILY_OF_EFFECT = {
    LifeEventEffect.CASH_OUT.value: LifeEventFamily.EXPENSES,
    LifeEventEffect.SKIP_NEXT_SALARY.value: LifeEventFamily.INCOME,
    LifeEventEffect.CASH_IN.value: LifeEventFamily.GOOD,
}


class LifeEventTypeDTO(BaseDTO):
    """Um tipo de imprevisto das regras da partida: o motor, o histórico e a tela leem a mesma lista."""

    key: str = Field(min_length=1, max_length=40)
    label: str = Field(min_length=1, max_length=LIFE_EVENT_LABEL_MAX_LENGTH)
    effect: LifeEventEffect
    family: LifeEventFamily
    # Chance relativa entre os tipos quando sai um imprevisto
    weight: int = Field(ge=1)
    # Quantas despesas mensais saem (ou entram) do caixa; a demissão não usa
    expense_multiple: Decimal = Field(ge=0, le=LIFE_EVENT_MAX_EXPENSE_MULTIPLE)
    enabled: bool

    @model_validator(mode="before")
    @classmethod
    def fill_family(cls, data: Any) -> Any:
        if isinstance(data, dict) and "family" not in data:
            effect = data.get("effect")
            effect = effect.value if isinstance(effect, LifeEventEffect) else effect
            if effect in _FAMILY_OF_EFFECT:
                return {**data, "family": _FAMILY_OF_EFFECT[effect]}
        return data


class LifeFrequenciesDTO(BaseDTO):
    """O quanto cada família de imprevistos sai; a geral (`unexpected_per_year`) vale com as três em Normal."""

    expenses: LifeFrequency = LifeFrequency.NORMAL
    income: LifeFrequency = LifeFrequency.NORMAL
    good: LifeFrequency = LifeFrequency.NORMAL

    def of(self, family: LifeEventFamily) -> LifeFrequency:
        match family:
            case LifeEventFamily.EXPENSES:
                return self.expenses
            case LifeEventFamily.INCOME:
                return self.income
            case LifeEventFamily.GOOD:
                return self.good


DEFAULT_LIFE_EVENTS: tuple[LifeEventTypeDTO, ...] = tuple(
    LifeEventTypeDTO(
        key=spec.key,
        label=spec.label,
        effect=spec.effect,
        family=spec.family,
        weight=spec.weight,
        expense_multiple=spec.expense_multiple,
        enabled=True,
    )
    for spec in LIFE_EVENT_CATALOG
)

# Os tipos que toda lista guarda: salas salvas antes do catálogo ampliado só têm estes
REQUIRED_LIFE_EVENT_KEYS = ("REPAIR", "HEALTH", "LAYOFF")


def validate_life_events(
    events: list[LifeEventTypeDTO],
) -> list[LifeEventTypeDTO]:
    """Os tipos de fábrica obrigatórios ficam sempre na lista (só se desligam) e as chaves não se repetem."""
    keys = [event.key for event in events]
    if len(set(keys)) != len(keys):
        raise ValueError("Cada tipo de imprevisto precisa de uma chave única.")
    if len(events) > LIFE_EVENTS_MAX_COUNT:
        raise ValueError(
            f"No máximo {LIFE_EVENTS_MAX_COUNT} tipos de imprevisto por partida."
        )
    for default in DEFAULT_LIFE_EVENTS:
        if default.key not in REQUIRED_LIFE_EVENT_KEYS:
            continue
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
    # Quanto saiu (ou entrou, no efeito CASH_IN) do caixa de cada jogador; zero na demissão, que tira o salário do mês seguinte
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
    # A variável que move a renda da profissão e o valor dela no dia; nulos nas outras
    driver: IncomeDriver | None = None
    driver_value: Decimal | None = None


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
