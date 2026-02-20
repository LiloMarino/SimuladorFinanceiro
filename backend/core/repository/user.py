from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Case, delete, func, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.user import UserDTO
from backend.core.models.models import (
    EventCashflow,
    EventEquity,
    EventFixedIncome,
    FixedIncomePosition,
    Snapshots,
    Users,
)


class UserRepository:
    @transactional
    def create_user(self, session: Session, client_id: UUID, nickname: str) -> UserDTO:
        user = Users(
            client_id=client_id,
            nickname=nickname,
            created_at=datetime.now(UTC),
        )
        session.add(user)
        session.flush()
        return UserDTO(
            id=user.id,
            client_id=user.client_id,
            nickname=user.nickname,
        )

    @transactional
    def get_by_client_id(self, session: Session, client_id: UUID) -> UserDTO | None:
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
    def get_user_balance(self, session: Session, client_id: UUID) -> float:
        # --------------------------------------------------
        # 1. Usuário
        # --------------------------------------------------
        user = session.execute(
            select(Users).where(Users.client_id == client_id)
        ).scalar_one()

        # --------------------------------------------------
        # 2. CASHFLOW (TOTAL)
        # --------------------------------------------------
        total_cash = Decimal(
            session.execute(
                select(
                    func.coalesce(
                        func.sum(
                            Case(
                                (
                                    EventCashflow.event_type.in_(
                                        ["DEPOSIT", "DIVIDEND"]
                                    ),
                                    EventCashflow.amount,
                                ),
                                (
                                    EventCashflow.event_type == "WITHDRAW",
                                    -EventCashflow.amount,
                                ),
                                else_=Decimal("0"),
                            )
                        ),
                        0,
                    )
                ).where(
                    EventCashflow.user_id == user.id,
                )
            ).scalar_one()
        )

        return float(total_cash)

    @transactional
    def get_all_users(self, session: Session) -> list[UserDTO]:
        users = session.execute(select(Users)).scalars().all()

        return [
            UserDTO(
                id=user.id,
                client_id=user.client_id,
                nickname=user.nickname,
            )
            for user in users
        ]

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

    @transactional
    def delete_user(self, session: Session, user_id: int) -> None:
        session.execute(delete(Users).where(Users.id == user_id))

    @transactional
    def reset_users_data(
        self, session: Session, event_date: date, starting_cash: float
    ) -> None:
        users = session.query(Users).all()

        # Deleta todos os dados anteriores
        session.query(EventCashflow).delete(synchronize_session=False)
        session.query(EventEquity).delete(synchronize_session=False)
        session.query(EventFixedIncome).delete(synchronize_session=False)
        session.query(FixedIncomePosition).delete(synchronize_session=False)
        session.query(Snapshots).delete(synchronize_session=False)

        # Cria um novo cashflow de depósito inicial para cada usuário
        now = datetime.now(UTC)
        new_cashflows = [
            EventCashflow(
                user_id=user.id,
                event_type="DEPOSIT",
                amount=starting_cash,
                event_date=event_date,
                created_at=now,
            )
            for user in users
        ]
        session.add_all(new_cashflows)
