from datetime import UTC, date, datetime

from sqlalchemy import func, insert, or_, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.summaries import SummaryDTO, YearReviewDTO
from backend.core.enum import SummaryKind
from backend.core.models.models import Snapshots, Summaries


def _summary_dto(row: Summaries) -> SummaryDTO:
    return SummaryDTO(
        id=row.id,
        game_date=row.game_date,
        content=YearReviewDTO.model_validate(row.content),
    )


class SummaryRepository:
    @transactional
    def create(
        self,
        session: Session,
        simulation_id: int,
        user_id: int,
        game_date: date,
        content: YearReviewDTO,
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
    def history_between(
        self,
        session: Session,
        simulation_id: int,
        portfolio_id: int,
        since: date,
        until: date,
    ) -> list[PatrimonialHistoryDTO]:
        """Os snapshots da carteira em [since, until], com o último de antes de `since` à frente."""
        previous = (
            select(func.max(Snapshots.snapshot_date))
            .where(
                Snapshots.simulation_id == simulation_id,
                Snapshots.portfolio_id == portfolio_id,
                Snapshots.snapshot_date < since,
            )
            .scalar_subquery()
        )
        rows = session.scalars(
            select(Snapshots)
            .where(
                Snapshots.simulation_id == simulation_id,
                Snapshots.portfolio_id == portfolio_id,
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
