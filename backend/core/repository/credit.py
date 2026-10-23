from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.events.credit import CreditEventDTO
from backend.core.enum import CreditEventType, CreditGrade, PrepaymentMode
from backend.core.models.models import EventCredit


def credit_event_dto(row: EventCredit) -> CreditEventDTO:
    return CreditEventDTO(
        simulation_id=row.simulation_id,
        user_id=row.user_id,
        loan_id=row.loan_id,
        event_type=CreditEventType(row.event_type),
        amount=row.amount,
        installment_number=row.installment_number,
        annual_rate=row.annual_rate,
        term_months=row.term_months,
        grade=CreditGrade(row.grade) if row.grade else None,
        prepayment_mode=(
            PrepaymentMode(row.prepayment_mode) if row.prepayment_mode else None
        ),
        event_date=row.event_date,
        created_at=row.created_at,
    )


class CreditRepository:
    @transactional
    def get_events(
        self, session: Session, simulation_id: int, user_id: int
    ) -> list[CreditEventDTO]:
        """Os eventos de crédito do jogador na ordem em que aconteceram."""
        rows = session.scalars(
            select(EventCredit)
            .where(
                EventCredit.simulation_id == simulation_id,
                EventCredit.user_id == user_id,
            )
            .order_by(EventCredit.id)
        ).all()
        return [credit_event_dto(row) for row in rows]
