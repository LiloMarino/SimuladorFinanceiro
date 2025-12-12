from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from backend import config
from backend.core.decorators.transactional_method import transactional
from backend.core.dto.user import UserDTO
from backend.core.models.models import EventCashflow, Users


class UserRepository:
    @transactional
    def create_user(self, session: Session, client_id: str, nickname: str) -> UserDTO:
        user = Users(
            client_id=client_id,
            nickname=nickname,
            created_at=datetime.now(UTC),
        )
        session.add(user)

        cash_event = EventCashflow(
            user_id=user.id,
            event_type="DEPOSIT",
            amount=config.toml.simulation.starting_cash,
            event_date=datetime.now(UTC).date(),
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
        ...

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
