from datetime import UTC, date, datetime
from decimal import Decimal

from pydantic import TypeAdapter
from sqlalchemy import func, insert, or_, select, update
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.inbox import (
    InboxContent,
    InboxEntryDTO,
    MonthSummaryDTO,
)
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.enum import CashflowEventType, InboxEntryKind
from backend.core.models.models import EventCashflow, InboxEntries, Snapshots

_content: TypeAdapter[InboxContent] = TypeAdapter(InboxContent)


def _entry_dto(row: InboxEntries) -> InboxEntryDTO:
    return InboxEntryDTO(
        id=row.id,
        game_date=row.game_date,
        room=row.user_id is None,
        read=row.read,
        content=_content.validate_python(row.content),
    )


def _visible_to(simulation_id: int, user_id: int):
    """As entradas do jogador e as da sala inteira."""
    return (InboxEntries.simulation_id == simulation_id) & or_(
        InboxEntries.user_id == user_id, InboxEntries.user_id.is_(None)
    )


class InboxRepository:
    @transactional
    def create(
        self,
        session: Session,
        simulation_id: int,
        user_id: int | None,
        game_date: date,
        content: InboxContent,
    ) -> InboxEntryDTO:
        row = session.scalars(
            insert(InboxEntries)
            .values(
                simulation_id=simulation_id,
                user_id=user_id,
                game_date=game_date,
                kind=InboxEntryKind(content.kind).value,
                content=content.to_json(),
                created_at=datetime.now(UTC),
            )
            .returning(InboxEntries)
        ).one()
        return _entry_dto(row)

    @transactional
    def entries(
        self, session: Session, simulation_id: int, user_id: int
    ) -> list[InboxEntryDTO]:
        """Da mais nova para a mais antiga."""
        rows = session.scalars(
            select(InboxEntries)
            .where(_visible_to(simulation_id, user_id))
            .order_by(InboxEntries.game_date.desc(), InboxEntries.id.desc())
        )
        return [_entry_dto(row) for row in rows]

    @transactional
    def mark_read(
        self, session: Session, simulation_id: int, user_id: int, entry_id: int
    ) -> bool:
        """Falso quando a entrada não é do jogador."""
        marked = session.scalar(
            update(InboxEntries)
            .where(
                InboxEntries.id == entry_id,
                InboxEntries.simulation_id == simulation_id,
                InboxEntries.user_id == user_id,
            )
            .values(read=True)
            .returning(InboxEntries.id)
        )
        return marked is not None

    @transactional
    def mark_all_read(self, session: Session, simulation_id: int, user_id: int) -> None:
        session.execute(
            update(InboxEntries)
            .where(
                InboxEntries.simulation_id == simulation_id,
                InboxEntries.user_id == user_id,
                InboxEntries.read.is_(False),
            )
            .values(read=True)
        )

    @transactional
    def month_summaries(
        self, session: Session, simulation_id: int, user_id: int, after: date
    ) -> list[MonthSummaryDTO]:
        """Os resumos do jogador entregues depois de `after`, em ordem."""
        rows = session.scalars(
            select(InboxEntries)
            .where(
                InboxEntries.simulation_id == simulation_id,
                InboxEntries.user_id == user_id,
                InboxEntries.kind == InboxEntryKind.MONTH_SUMMARY.value,
                InboxEntries.game_date > after,
            )
            .order_by(InboxEntries.game_date, InboxEntries.id)
        )
        return [MonthSummaryDTO.model_validate(row.content) for row in rows]

    @transactional
    def last_month_summary(
        self, session: Session, simulation_id: int, user_id: int
    ) -> MonthSummaryDTO | None:
        row = session.scalars(
            select(InboxEntries)
            .where(
                InboxEntries.simulation_id == simulation_id,
                InboxEntries.user_id == user_id,
                InboxEntries.kind == InboxEntryKind.MONTH_SUMMARY.value,
            )
            .order_by(InboxEntries.game_date.desc(), InboxEntries.id.desc())
            .limit(1)
        ).first()
        return MonthSummaryDTO.model_validate(row.content) if row else None

    @transactional
    def history_between(
        self,
        session: Session,
        simulation_id: int,
        user_id: int,
        since: date,
        until: date,
    ) -> list[PatrimonialHistoryDTO]:
        """Os snapshots do jogador em [since, until], com o último de antes de `since` à frente."""
        previous = (
            select(func.max(Snapshots.snapshot_date))
            .where(
                Snapshots.simulation_id == simulation_id,
                Snapshots.user_id == user_id,
                Snapshots.snapshot_date < since,
            )
            .scalar_subquery()
        )
        rows = session.scalars(
            select(Snapshots)
            .where(
                Snapshots.simulation_id == simulation_id,
                Snapshots.user_id == user_id,
                or_(
                    Snapshots.snapshot_date.between(since, until),
                    Snapshots.snapshot_date == previous,
                ),
            )
            .order_by(Snapshots.snapshot_date)
        )
        return [
            PatrimonialHistoryDTO.model_validate(row, from_attributes=True)
            for row in rows
        ]

    @transactional
    def cashflow_totals(
        self,
        session: Session,
        simulation_id: int,
        user_id: int,
        start: date,
        end: date,
    ) -> dict[CashflowEventType, Decimal]:
        """O total de cada tipo de evento de caixa do jogador em [start, end]."""
        rows = session.execute(
            select(EventCashflow.event_type, func.sum(EventCashflow.amount))
            .where(
                EventCashflow.simulation_id == simulation_id,
                EventCashflow.user_id == user_id,
                EventCashflow.event_date.between(start, end),
            )
            .group_by(EventCashflow.event_type)
        ).all()
        return {CashflowEventType(kind): Decimal(total) for kind, total in rows}
