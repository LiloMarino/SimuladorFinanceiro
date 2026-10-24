from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.events.government import GovernmentEventDTO
from backend.core.enum import GovernmentEventType
from backend.core.models.models import GovernmentEvent


class GovernmentRepository:
    @transactional
    def insert(self, session: Session, event: GovernmentEventDTO) -> None:
        session.add(
            GovernmentEvent(
                simulation_id=event.simulation_id,
                event_type=event.event_type.value,
                payload=event.payload,
                event_date=event.event_date,
                created_at=event.created_at,
            )
        )

    @transactional
    def get_events(
        self, session: Session, simulation_id: int
    ) -> list[GovernmentEventDTO]:
        """Os eventos da partida na ordem em que aconteceram."""
        rows = session.scalars(
            select(GovernmentEvent)
            .where(GovernmentEvent.simulation_id == simulation_id)
            .order_by(GovernmentEvent.id)
        ).all()
        return [
            GovernmentEventDTO(
                simulation_id=row.simulation_id,
                event_type=GovernmentEventType(row.event_type),
                payload=row.payload,
                event_date=row.event_date,
                created_at=row.created_at,
            )
            for row in rows
        ]
