from collections import defaultdict

from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.events.fixed_income import FixedIncomeEventDTO
from backend.core.models.models import EventCashflow, EventEquity, EventFixedIncome


class EventRepository:
    @transactional
    def insert_many(self, session: Session, events: list[BaseEventDTO]) -> None:
        if not events:
            return

        buckets = defaultdict(list)

        for event in events:
            buckets[type(event)].append(event)

        if CashflowEventDTO in buckets:
            self._insert_cashflows(session, buckets[CashflowEventDTO])

        if EquityEventDTO in buckets:
            self._insert_equities(session, buckets[EquityEventDTO])

        if FixedIncomeEventDTO in buckets:
            self._insert_fixed_income(session, buckets[FixedIncomeEventDTO])

    def _insert_cashflows(
        self, session: Session, cashflow_events: list[CashflowEventDTO]
    ) -> None:
        cashflow_models = [
            EventCashflow(
                user_id=e.user_id,
                event_type=e.event_type.value,
                amount=e.amount,
                event_date=e.event_date,
                created_at=e.created_at,
            )
            for e in cashflow_events
        ]
        session.bulk_save_objects(cashflow_models)

    def _insert_equities(
        self, session: Session, equity_events: list[EquityEventDTO]
    ) -> None:
        equity_models = [
            EventEquity(
                user_id=e.user_id,
                stock_id=e.stock_id,
                event_type=e.event_type.value,
                quantity=e.quantity,
                price=e.price,
                event_date=e.event_date,
                created_at=e.created_at,
            )
            for e in equity_events
        ]
        session.bulk_save_objects(equity_models)

    def _insert_fixed_income(
        self, session: Session, fixed_income_events: list[FixedIncomeEventDTO]
    ) -> None:
        fixed_income_models = [
            EventFixedIncome(
                user_id=e.user_id,
                asset_id=e.asset_id,
                event_type=e.event_type.value,
                amount=e.amount,
                event_date=e.event_date,
                created_at=e.created_at,
            )
            for e in fixed_income_events
        ]
        session.bulk_save_objects(fixed_income_models)
