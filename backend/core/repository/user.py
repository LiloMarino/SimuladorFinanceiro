from datetime import UTC, datetime
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
    def get_user_balance(self, session: Session, portfolio_id: int) -> Decimal:
        """O caixa da carteira: a soma dos eventos de caixa dela na partida ativa."""
        simulation_id = SimulationManager.get_active_simulation_id()
        return Decimal(
            session.execute(
                select(cash_delta()).where(
                    EventCashflow.portfolio_id == portfolio_id,
                    EventCashflow.simulation_id == simulation_id,
                )
            ).scalar_one()
        )

    @transactional
    def get_total_cashflow(
        self, session: Session, portfolio_id: int, event_type: CashflowEventType
    ) -> Decimal:
        simulation_id = SimulationManager.get_active_simulation_id()
        return Decimal(
            session.execute(
                select(func.coalesce(func.sum(EventCashflow.amount), 0)).where(
                    EventCashflow.portfolio_id == portfolio_id,
                    EventCashflow.simulation_id == simulation_id,
                    EventCashflow.event_type == event_type.value,
                )
            ).scalar_one()
        )

    @transactional
    def get_total_contribution(self, session: Session, portfolio_id: int) -> Decimal:
        """Capital que a carteira recebeu além do saldo inicial: aportes, salários, despesas e imprevistos."""
        simulation_id = SimulationManager.get_active_simulation_id()
        return Decimal(
            session.execute(
                select(cash_delta(CONTRIBUTION_TYPES)).where(
                    EventCashflow.portfolio_id == portfolio_id,
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
