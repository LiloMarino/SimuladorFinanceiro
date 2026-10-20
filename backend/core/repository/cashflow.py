from collections.abc import Iterable
from decimal import Decimal

from sqlalchemy import ColumnElement, case, func

from backend.core.enum import CashflowEventType
from backend.core.models.models import EventCashflow


def cash_delta(
    types: Iterable[CashflowEventType] = CashflowEventType,
) -> ColumnElement[Decimal]:
    """Soma do efeito dos eventos de `types` no caixa: o valor com o sinal do tipo."""
    chosen = list(types)
    inflow = [t.value for t in chosen if t.sign > 0]
    outflow = [t.value for t in chosen if t.sign < 0]
    return func.coalesce(
        func.sum(
            case(
                (EventCashflow.event_type.in_(inflow), EventCashflow.amount),
                (EventCashflow.event_type.in_(outflow), -EventCashflow.amount),
                else_=Decimal(0),
            )
        ),
        0,
    )
