from collections import defaultdict
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.events.fixed_income import FixedIncomeEventDTO
from backend.core.models.models import (
    EventCashflow,
    EventEquity,
    EventFixedIncome,
    Stock,
)


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

    @transactional
    def get_last_event_date(self, session: Session, simulation_id: int) -> date | None:
        """Data do evento mais recente da simulação, em qualquer tabela de evento."""
        dates = [
            session.execute(
                select(func.max(model.event_date)).where(
                    model.simulation_id == simulation_id
                )
            ).scalar_one_or_none()
            for model in (EventCashflow, EventEquity, EventFixedIncome)
        ]
        return max((d for d in dates if d is not None), default=None)

    def _insert_cashflows(
        self, session: Session, cashflow_events: list[CashflowEventDTO]
    ) -> None:
        cashflow_models = [
            EventCashflow(
                simulation_id=e.simulation_id,
                user_id=e.user_id,
                event_type=e.event_type.value,
                amount=e.amount,
                event_date=e.event_date,
                created_at=e.created_at,
            )
            for e in cashflow_events
        ]
        session.add_all(cashflow_models)

    def _insert_equities(
        self, session: Session, equity_events: list[EquityEventDTO]
    ) -> None:
        tickers = {e.ticker for e in equity_events}

        stocks = session.query(Stock).filter(Stock.ticker.in_(tickers)).all()
        stock_map = {s.ticker: s.id for s in stocks}

        equity_models = [
            EventEquity(
                simulation_id=e.simulation_id,
                user_id=e.user_id,
                stock_id=stock_map[e.ticker],
                event_type=e.event_type.value,
                quantity=e.quantity,
                price=e.price,
                event_date=e.event_date,
                created_at=e.created_at,
            )
            for e in equity_events
        ]
        session.add_all(equity_models)

    def _insert_fixed_income(
        self, session: Session, fixed_income_events: list[FixedIncomeEventDTO]
    ) -> None:
        fixed_income_models = [
            EventFixedIncome(
                simulation_id=e.simulation_id,
                user_id=e.user_id,
                asset_id=e.asset_id,
                event_type=e.event_type.value,
                amount=e.amount,
                event_date=e.event_date,
                created_at=e.created_at,
            )
            for e in fixed_income_events
        ]
        session.add_all(fixed_income_models)
