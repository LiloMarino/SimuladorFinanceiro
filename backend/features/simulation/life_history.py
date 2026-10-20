"""
Histórico do viver de renda: os imprevistos, as demissões e o cheque especial de
um jogador, montados dos eventos de caixa. Entrar e sair do cheque especial não é
evento gravado: sai do saldo reconstruído evento a evento.
"""

from decimal import Decimal

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
) -> LifeHistoryPageDTO:
    """Uma página do mais recente ao mais antigo, com a contagem de cada categoria."""
    chosen = [r for r in reversed(rows) if category is None or r.category is category]

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
