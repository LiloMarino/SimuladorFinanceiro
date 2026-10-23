from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.user import UserDTO
from backend.core.enum import CONTRIBUTION_TYPES, CashflowEventType
from backend.core.models.models import (
    EventCashflow,
    Users,
)
from backend.core.repository.cashflow import cash_delta
from backend.core.runtime.simulation_manager import SimulationManager


def user_dto(user: Users) -> UserDTO:
    return UserDTO(
        id=user.id,
        client_id=user.client_id,
        nickname=user.nickname,
        is_bot=user.is_bot,
    )


class UserRepository:
    @transactional
    def create_user(
        self, session: Session, client_id: UUID, nickname: str, *, is_bot: bool = False
    ) -> UserDTO:
        user = Users(
            client_id=client_id,
            nickname=nickname,
            is_bot=is_bot,
            created_at=datetime.now(UTC),
        )
        session.add(user)
        session.flush()
        return user_dto(user)

    @transactional
    def get_by_client_id(self, session: Session, client_id: UUID) -> UserDTO | None:
        user = session.execute(
            select(Users).where(Users.client_id == client_id)
        ).scalar_one_or_none()
        return user_dto(user) if user else None

    @transactional
    def get_by_nickname(self, session: Session, nickname: str) -> UserDTO | None:
        """A pessoa com esse apelido: bot não é dono de apelido, então nunca entra aqui."""
        user = session.execute(
            select(Users).where(Users.nickname == nickname, Users.is_bot.is_(False))
        ).scalar_one_or_none()
        return user_dto(user) if user else None

    @transactional
    def get_user_balance(self, session: Session, client_id: UUID) -> Decimal:
        simulation_id = SimulationManager.get_active_simulation_id()

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
                select(cash_delta()).where(
                    EventCashflow.user_id == user.id,
                    EventCashflow.simulation_id == simulation_id,
                )
            ).scalar_one()
        )

        return total_cash

    @transactional
    def get_total_cashflow(
        self, session: Session, user_id: int, event_type: CashflowEventType
    ) -> Decimal:
        simulation_id = SimulationManager.get_active_simulation_id()
        return Decimal(
            session.execute(
                select(func.coalesce(func.sum(EventCashflow.amount), 0)).where(
                    EventCashflow.user_id == user_id,
                    EventCashflow.simulation_id == simulation_id,
                    EventCashflow.event_type == event_type.value,
                )
            ).scalar_one()
        )

    @transactional
    def get_total_contribution(self, session: Session, user_id: int) -> Decimal:
        """Capital que o jogador pôs além do saldo inicial: aportes, salários, despesas e imprevistos."""
        simulation_id = SimulationManager.get_active_simulation_id()
        return Decimal(
            session.execute(
                select(cash_delta(CONTRIBUTION_TYPES)).where(
                    EventCashflow.user_id == user_id,
                    EventCashflow.simulation_id == simulation_id,
                )
            ).scalar_one()
        )

    @transactional
    def update_client_id(
        self, session: Session, user_id: int, new_client_id: UUID
    ) -> UserDTO:
        user = session.execute(select(Users).where(Users.id == user_id)).scalar_one()
        user.client_id = new_client_id

        return user_dto(user)

    @transactional
    def rename(self, session: Session, user_id: int, nickname: str) -> UserDTO:
        user = session.execute(select(Users).where(Users.id == user_id)).scalar_one()
        user.nickname = nickname
        return user_dto(user)

    @transactional
    def delete_user(self, session: Session, user_id: int) -> None:
        session.execute(delete(Users).where(Users.id == user_id))

    @transactional
    def seed_simulation_users(
        self,
        session: Session,
        simulation_id: int,
        user_ids: list[int],
        event_date: date,
        starting_cash: Decimal,
    ) -> None:
        now = datetime.now(UTC)
        new_cashflows = [
            EventCashflow(
                simulation_id=simulation_id,
                user_id=user_id,
                event_type="DEPOSIT",
                amount=starting_cash,
                event_date=event_date,
                created_at=now,
            )
            for user_id in user_ids
        ]
        session.add_all(new_cashflows)
