"""
Histórico do viver de renda: os imprevistos, as demissões e o cheque especial de
um jogador, montados dos eventos de caixa. Entrar e sair do cheque especial não é
evento gravado: sai do saldo reconstruído evento a evento.
"""

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
    LifeEventEffect,
    LifeHistoryCategory,
    LifeHistoryKind,
    LifeHistorySort,
)
from backend.features.simulation.life_events import LIFE_EVENTS_BY_KEY


def build_history(events: list[CashflowEventDTO]) -> list[LifeHistoryRowDTO]:
    """
    As linhas do mais antigo ao mais novo, a partir de todos os eventos de caixa do
    jogador em ordem. O juro é cobrado por pregão e vira uma linha por mês, datada
    do último pregão cobrado nele.
    """
    rows: list[LifeHistoryRowDTO] = []
    interest: LifeHistoryRowDTO | None = None
    cash = Decimal(0)

    def flush_interest() -> None:
        nonlocal interest
        if interest is not None:
            rows.append(interest)
            interest = None

    for event in events:
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
            rows.append(_unexpected_row(event, cash))

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
            return f"salário de {months[row.event_date.month % 12]} não entrou"
        case LifeHistoryKind.OVERDRAFT_STARTED:
            return "caixa ficou negativo"
        case LifeHistoryKind.OVERDRAFT_ENDED:
            return "caixa voltou ao positivo"
        case LifeHistoryKind.OVERDRAFT_INTEREST:
            return "juros"


def _unexpected_row(event: CashflowEventDTO, cash: Decimal) -> LifeHistoryRowDTO:
    kind = LIFE_EVENTS_BY_KEY.get(event.life_event_key or "")
    if kind is not None and kind.effect is LifeEventEffect.SKIP_NEXT_SALARY:
        return _row(
            event, LifeHistoryCategory.LAYOFF, LifeHistoryKind.LAYOFF, cash, kind.label
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
