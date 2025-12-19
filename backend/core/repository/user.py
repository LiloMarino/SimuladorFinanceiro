from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Case, func
from sqlalchemy.orm import Session

from backend import config
from backend.core.decorators.transactional_method import transactional
from backend.core.dto.user import UserDTO
from backend.core.models.models import EventCashflow, Snapshots, Users


class UserRepository:
    @transactional
    def create_user(
        self, session: Session, client_id: str, nickname: str, event_date: datetime
    ) -> UserDTO:
        user = Users(
            client_id=client_id,
            nickname=nickname,
            created_at=datetime.now(UTC),
        )
        session.add(user)
        session.flush()
        cash_event = EventCashflow(
            user_id=user.id,
            event_type="DEPOSIT",
            amount=config.toml.simulation.starting_cash,
            event_date=event_date.date(),
            created_at=datetime.now(UTC),
        )
        session.add(cash_event)

        return UserDTO(
            id=user.id,
            client_id=user.client_id,
            nickname=user.nickname,
        )

    @transactional
    def get_by_client_id(self, session: Session, client_id: str) -> UserDTO | None:
        user = session.query(Users).filter_by(client_id=client_id).first()
        if not user:
            return None

        return UserDTO(
            id=user.id,
            client_id=user.client_id,
            nickname=user.nickname,
        )

    @transactional
    def get_by_nickname(self, session: Session, nickname: str) -> UserDTO | None:
        user = session.query(Users).filter_by(nickname=nickname).first()
        if not user:
            return None

        return UserDTO(
            id=user.id,
            client_id=user.client_id,
            nickname=user.nickname,
        )

    @transactional
    def get_user_balance(self, session: Session, client_id: str) -> float:
        user = session.query(Users).filter_by(client_id=client_id).one()
        user_id = user.id

        # Último snapshot
        last_snapshot = (
            session.query(Snapshots)
            .filter_by(user_id=user_id)
            .order_by(Snapshots.snapshot_date.desc())
            .first()
        )

        balance = float(last_snapshot.total_cash) if last_snapshot else 0.0
        snapshot_date = last_snapshot.snapshot_date if last_snapshot else None

        # Soma eventos após snapshot
        event_sum_query = session.query(
            func.coalesce(
                func.sum(
                    Case(
                        (EventCashflow.event_type == "DEPOSIT", EventCashflow.amount),
                        (EventCashflow.event_type == "DIVIDEND", EventCashflow.amount),
                        (EventCashflow.event_type == "WITHDRAW", -EventCashflow.amount),
                        else_=0,
                    )
                ),
                0,
            )
        ).filter(EventCashflow.user_id == user_id)

        if snapshot_date:
            event_sum_query = event_sum_query.filter(
                EventCashflow.event_date > snapshot_date
            )

        balance += float(event_sum_query.scalar())

        return balance

    @transactional
    def update_client_id(
        self, session: Session, user_id: int, new_client_id: UUID
    ) -> UserDTO:
        user = session.query(Users).filter_by(id=user_id).one()
        user.client_id = new_client_id

        return UserDTO(
            id=user.id,
            client_id=user.client_id,
            nickname=user.nickname,
        )
