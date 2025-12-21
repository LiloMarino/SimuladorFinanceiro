from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Case, func, select
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
        # --------------------------------------------------
        # 1. Usuário
        # --------------------------------------------------
        user = session.execute(
            select(Users).where(Users.client_id == client_id)
        ).scalar_one()

        snapshot_date: date | None = None

        # --------------------------------------------------
        # 2. Último snapshot
        # --------------------------------------------------
        last_snapshot = session.execute(
            select(Snapshots)
            .where(Snapshots.user_id == user.id)
            .order_by(Snapshots.snapshot_date.desc())
            .limit(1)
        ).scalar_one_or_none()
        if last_snapshot:
            base_cash = last_snapshot.total_cash
            snapshot_date = last_snapshot.snapshot_date
        else:
            base_cash = Decimal("0")

        # --------------------------------------------------
        # 3. CASHFLOW incremental
        # --------------------------------------------------
        cash_delta = session.execute(
            select(
                func.coalesce(
                    func.sum(
                        Case(
                            (
                                EventCashflow.event_type == "DEPOSIT",
                                EventCashflow.amount,
                            ),
                            (
                                EventCashflow.event_type == "DIVIDEND",
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
                *([EventCashflow.event_date > snapshot_date] if snapshot_date else []),
            )
        ).scalar_one()

        total_cash = base_cash + Decimal(cash_delta)

        return float(total_cash)

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
