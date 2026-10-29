from datetime import UTC, date, datetime
from decimal import Decimal

from pydantic import TypeAdapter
from sqlalchemy import func, insert, or_, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.summaries import (
    MonthSummaryDTO,
    SummaryContent,
    SummaryDTO,
)
from backend.core.enum import CashflowEventType, SummaryKind
from backend.core.models.models import EventCashflow, Snapshots, Summaries

_content: TypeAdapter[SummaryContent] = TypeAdapter(SummaryContent)


def _summary_dto(row: Summaries) -> SummaryDTO:
    return SummaryDTO(
        id=row.id,
        game_date=row.game_date,
        content=_content.validate_python(row.content),
    )


class SummaryRepository:
    @transactional
    def create(
        self,
        session: Session,
        simulation_id: int,
        user_id: int,
        game_date: date,
        content: SummaryContent,
    ) -> SummaryDTO:
        row = session.scalars(
            insert(Summaries)
            .values(
                simulation_id=simulation_id,
                user_id=user_id,
                game_date=game_date,
                kind=SummaryKind(content.kind).value,
                content=content.to_json(),
                created_at=datetime.now(UTC),
            )
            .returning(Summaries)
        ).one()
        return _summary_dto(row)

    @transactional
    def of_player(
        self, session: Session, simulation_id: int, user_id: int
    ) -> list[SummaryDTO]:
        """Do mais novo para o mais antigo."""
        rows = session.scalars(
            select(Summaries)
            .where(
                Summaries.simulation_id == simulation_id,
                Summaries.user_id == user_id,
            )
            .order_by(Summaries.game_date.desc(), Summaries.id.desc())
        )
        return [_summary_dto(row) for row in rows]

    @transactional
    def month_summaries(
        self, session: Session, simulation_id: int, user_id: int, after: date
    ) -> list[MonthSummaryDTO]:
        """Os resumos do jogador entregues depois de `after`, em ordem."""
        rows = session.scalars(
            select(Summaries)
            .where(
                Summaries.simulation_id == simulation_id,
                Summaries.user_id == user_id,
                Summaries.kind == SummaryKind.MONTH_SUMMARY.value,
                Summaries.game_date > after,
            )
            .order_by(Summaries.game_date, Summaries.id)
        )
        return [MonthSummaryDTO.model_validate(row.content) for row in rows]

    @transactional
    def last_month_summary(
        self, session: Session, simulation_id: int, user_id: int
    ) -> MonthSummaryDTO | None:
        row = session.scalars(
            select(Summaries)
            .where(
                Summaries.simulation_id == simulation_id,
                Summaries.user_id == user_id,
                Summaries.kind == SummaryKind.MONTH_SUMMARY.value,
            )
            .order_by(Summaries.game_date.desc(), Summaries.id.desc())
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
