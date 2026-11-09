"""
Histórico do viver de renda: os imprevistos, as demissões e o cheque especial de
um jogador, montados dos eventos de caixa. Entrar e sair do cheque especial não é
evento gravado: sai do saldo reconstruído evento a evento. As mudanças de salário,
despesa e juro do cheque especial, com a origem na economia da partida, vêm do
orçamento e entram na ordem das datas.
"""

from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Literal

from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.life import (
    LifeHistoryCountsDTO,
    LifeHistoryPageDTO,
    LifeHistoryRowDTO,
)
from backend.core.enum import (
    CashflowEventType,
    IndicatorSeries,
    LifeEventEffect,
    LifeHistoryCategory,
    LifeHistoryKind,
    LifeHistorySort,
)
from backend.core.indicators import annual_index_rate
from backend.core.life_budget import LifeBudget
from backend.core.utils import format_money
from backend.features.simulation.life_events import (
    LIFE_EVENTS_BY_KEY,
    net_salary,
)
from backend.features.tax_policy import DEFAULT_TAX_POLICY


@dataclass(frozen=True)
class BudgetChange:
    """Uma mudança do orçamento num dia, com o valor novo e a origem no rótulo."""

    day: date
    kind: LifeHistoryKind
    label: str


def budget_changes(
    life: LifeBudget,
    until: date,
    personal_rate_on: Callable[[date], Decimal],
    overdraft_rate_on: Callable[[date], Decimal],
) -> list[BudgetChange]:
    """
    Cada reajuste de salário e despesa, cada mudança da alíquota do IR das pessoas e
    cada mudança do juro do cheque especial (a taxa mensal mostrada com uma casa)
    até `until`. O juro e o IR são lidos no primeiro dia de cada mês.
    """
    changes: list[BudgetChange] = []
    for anniversary in life.readjustments(until)[1:]:
        ipca, growth = life.salary_raise_inputs(anniversary)
        origin = (
            f"IPCA de {_percent(ipca)} e PIB de {_percent(growth)}"
            if growth > 0
            else f"IPCA de {_percent(ipca)}, sem reajuste real (PIB de {_percent(growth)})"
        )
        salary = format_money(life.salary_on(anniversary))
        expense = format_money(life.expense_on(anniversary))
        changes.append(
            BudgetChange(
                anniversary,
                LifeHistoryKind.SALARY_READJUSTED,
                f"Salário base reajustado para {salary}: {origin}",
            )
        )
        changes.append(
            BudgetChange(
                anniversary,
                LifeHistoryKind.EXPENSE_READJUSTED,
                f"Despesa reajustada para {expense}: IPCA de {_percent(ipca)}",
            )
        )

    reference = DEFAULT_TAX_POLICY.personal_rate
    personal_rate = reference
    shown_rate: Decimal | None = None
    for day in _month_starts(life.start_date, until):
        rate = overdraft_rate_on(day)
        if round(rate * 100, 1) != shown_rate:
            shown_rate = round(rate * 100, 1)
            selic = annual_index_rate(IndicatorSeries.SELIC, day)
            changes.append(
                BudgetChange(
                    day,
                    LifeHistoryKind.OVERDRAFT_RATE_CHANGED,
                    f"Juro do cheque especial a {_percent(rate)} ao mês: SELIC de {_percent(selic)} ao ano",
                )
            )
        current = personal_rate_on(day)
        if current != personal_rate:
            personal_rate = current
            net = format_money(net_salary(life.salary_on(day), current))
            changes.append(
                BudgetChange(
                    day,
                    LifeHistoryKind.SALARY_TAX_CHANGED,
                    f"IR das pessoas em {_percent(current)} (referência de {_percent(reference)}): salário líquido de {net}",
                )
            )
    return sorted(changes, key=lambda change: change.day)


def build_history(
    events: list[CashflowEventDTO],
    changes: Sequence[BudgetChange] = (),
    unemployment_on: Callable[[date], Decimal] | None = None,
) -> list[LifeHistoryRowDTO]:
    """
    As linhas do mais antigo ao mais novo, a partir de todos os eventos de caixa do
    jogador em ordem e das mudanças do orçamento, na ordem das datas. O juro é
    cobrado por pregão e vira uma linha por mês, datada do último pregão cobrado
    nele. Com `unemployment_on`, a demissão cita o desemprego do dia.
    """
    rows: list[LifeHistoryRowDTO] = []
    interest: LifeHistoryRowDTO | None = None
    cash = Decimal(0)
    pending = iter(sorted(changes, key=lambda change: change.day))
    upcoming = next(pending, None)

    def flush_interest() -> None:
        nonlocal interest
        if interest is not None:
            rows.append(interest)
            interest = None

    for event in events:
        # As mudanças do orçamento até o dia do evento entram antes dele
        while upcoming is not None and upcoming.day <= event.event_date:
            rows.append(_budget_row(upcoming, cash))
            upcoming = next(pending, None)
        before = cash
        cash += event.event_type.sign * event.amount

        if event.event_type is CashflowEventType.OVERDRAFT_INTEREST:
            same_month = interest is not None and (
                (interest.event_date.year, interest.event_date.month)
                == (event.event_date.year, event.event_date.month)
            )
            if not same_month:
                flush_interest()
            previous = (
                interest.amount
                if interest is not None and interest.amount is not None
                else Decimal(0)
            )
            interest = _row(
                event,
                LifeHistoryCategory.OVERDRAFT,
                LifeHistoryKind.OVERDRAFT_INTEREST,
                cash,
                amount=previous - event.amount,
            )
            continue

        if event.event_type is CashflowEventType.UNEXPECTED_EXPENSE:
            flush_interest()
            rows.append(_unexpected_row(event, cash, unemployment_on))

        if before >= 0 > cash:
            flush_interest()
            rows.append(
                _row(
                    event,
                    LifeHistoryCategory.OVERDRAFT,
                    LifeHistoryKind.OVERDRAFT_STARTED,
                    cash,
                )
            )
        elif before < 0 <= cash:
            flush_interest()
            rows.append(
                _row(
                    event,
                    LifeHistoryCategory.OVERDRAFT,
                    LifeHistoryKind.OVERDRAFT_ENDED,
                    cash,
                )
            )

    flush_interest()
    while upcoming is not None:
        rows.append(_budget_row(upcoming, cash))
        upcoming = next(pending, None)
    return rows


def history_page(
    rows: list[LifeHistoryRowDTO],
    category: LifeHistoryCategory | None,
    offset: int,
    limit: int,
    sort_by: LifeHistorySort = LifeHistorySort.DATE,
    sort_direction: Literal["asc", "desc"] = "desc",
) -> LifeHistoryPageDTO:
    """Filtra e ordena o histórico inteiro antes de recortar a página."""
    chosen = [r for r in reversed(rows) if category is None or r.category is category]
    kinds = {
        LifeHistoryKind.UNEXPECTED_EXPENSE: "Imprevisto",
        LifeHistoryKind.LAYOFF: "Demissão",
        LifeHistoryKind.OVERDRAFT_STARTED: "Cheque especial",
        LifeHistoryKind.OVERDRAFT_ENDED: "Cheque especial",
        LifeHistoryKind.OVERDRAFT_INTEREST: "Cheque especial",
        LifeHistoryKind.SALARY_READJUSTED: "Salário",
        LifeHistoryKind.EXPENSE_READJUSTED: "Despesa",
        LifeHistoryKind.SALARY_TAX_CHANGED: "Salário",
        LifeHistoryKind.OVERDRAFT_RATE_CHANGED: "Cheque especial",
    }
    getters = {
        LifeHistorySort.DATE: lambda r: r.event_date,
        LifeHistorySort.TYPE: lambda r: kinds[r.kind].casefold(),
        LifeHistorySort.DESCRIPTION: _description_key,
        LifeHistorySort.AMOUNT: lambda r: r.amount,
        LifeHistorySort.CASH: lambda r: r.cash_after,
    }
    key = getters[sort_by]
    present = [r for r in chosen if key(r) is not None]
    absent = [r for r in chosen if key(r) is None]
    chosen = sorted(present, key=key, reverse=sort_direction == "desc") + absent

    def count(c: LifeHistoryCategory) -> int:
        return sum(1 for r in rows if r.category is c)

    return LifeHistoryPageDTO(
        items=chosen[offset : offset + limit],
        total=len(chosen),
        counts=LifeHistoryCountsDTO(
            all=len(rows),
            unexpected=count(LifeHistoryCategory.UNEXPECTED),
            layoff=count(LifeHistoryCategory.LAYOFF),
            overdraft=count(LifeHistoryCategory.OVERDRAFT),
            budget=count(LifeHistoryCategory.BUDGET),
        ),
        interest_paid=-sum(
            (
                r.amount
                for r in rows
                if r.kind is LifeHistoryKind.OVERDRAFT_INTEREST and r.amount is not None
            ),
            Decimal(0),
        ),
    )


def _description_key(row: LifeHistoryRowDTO) -> str:
    """Mesmos textos da coluna de descrição; a taxa de juros é igual em todas as linhas."""
    months = (
        "janeiro",
        "fevereiro",
        "março",
        "abril",
        "maio",
        "junho",
        "julho",
        "agosto",
        "setembro",
        "outubro",
        "novembro",
        "dezembro",
    )
    match row.kind:
        case LifeHistoryKind.UNEXPECTED_EXPENSE:
            return (row.label or "Imprevisto").casefold()
        case LifeHistoryKind.LAYOFF:
            text = f"salário de {months[row.event_date.month % 12]} não entrou"
            return f"{text} · {row.label.casefold()}" if row.label else text
        case LifeHistoryKind.OVERDRAFT_STARTED:
            return "caixa ficou negativo"
        case LifeHistoryKind.OVERDRAFT_ENDED:
            return "caixa voltou ao positivo"
        case LifeHistoryKind.OVERDRAFT_INTEREST:
            return "juros"
        case (
            LifeHistoryKind.SALARY_READJUSTED
            | LifeHistoryKind.EXPENSE_READJUSTED
            | LifeHistoryKind.SALARY_TAX_CHANGED
            | LifeHistoryKind.OVERDRAFT_RATE_CHANGED
        ):
            return (row.label or "").casefold()


def _unexpected_row(
    event: CashflowEventDTO,
    cash: Decimal,
    unemployment_on: Callable[[date], Decimal] | None,
) -> LifeHistoryRowDTO:
    kind = LIFE_EVENTS_BY_KEY.get(event.life_event_key or "")
    if kind is not None and kind.effect is LifeEventEffect.SKIP_NEXT_SALARY:
        label = (
            kind.label
            if unemployment_on is None
            else f"Desemprego de {_percent(unemployment_on(event.event_date))}"
        )
        return _row(
            event, LifeHistoryCategory.LAYOFF, LifeHistoryKind.LAYOFF, cash, label
        )
    return _row(
        event,
        LifeHistoryCategory.UNEXPECTED,
        LifeHistoryKind.UNEXPECTED_EXPENSE,
        cash,
        kind.label if kind else event.life_event_key,
        amount=-event.amount,
    )


def _row(
    event: CashflowEventDTO,
    category: LifeHistoryCategory,
    kind: LifeHistoryKind,
    cash: Decimal,
    label: str | None = None,
    amount: Decimal | None = None,
) -> LifeHistoryRowDTO:
    return LifeHistoryRowDTO(
        event_date=event.event_date,
        category=category,
        kind=kind,
        life_event_key=event.life_event_key,
        label=label,
        amount=amount,
        cash_after=cash,
    )


def _budget_row(change: BudgetChange, cash: Decimal) -> LifeHistoryRowDTO:
    return LifeHistoryRowDTO(
        event_date=change.day,
        category=LifeHistoryCategory.BUDGET,
        kind=change.kind,
        label=change.label,
        cash_after=cash,
    )


def _month_starts(start: date, until: date) -> Iterator[date]:
    """O dia do início e o dia 1 de cada mês seguinte, até `until`."""
    day = start
    while day <= until:
        yield day
        day = (day.replace(day=1) + timedelta(days=32)).replace(day=1)


def _percent(value: Decimal) -> str:
    """Fração em percentual com uma casa e vírgula: 0.0315 vira 3,2%."""
    return f"{value * 100:.1f}".replace(".", ",") + "%"
