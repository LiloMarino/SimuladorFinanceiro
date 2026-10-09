from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Case, func, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.snapshot import SnapshotDTO
from backend.core.models.models import (
    EventCashflow,
    FixedIncomePosition,
    Snapshots,
)
from backend.core.runtime.simulation_manager import SimulationManager


class SnapshotRepository:
    @transactional
    def create_snapshot(
        self,
        session: Session,
        user_id: int,
        snapshot_date: date,
        total_equity: Decimal,
    ) -> SnapshotDTO:
        """
        `total_equity` vem do motor: é o valor das ações ao preço negociado na
        simulação, que difere do histórico quando o impacto de preço está ligado.
        """
        simulation_id = SimulationManager.get_active_simulation_id()

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
                                        ["DEPOSIT", "DIVIDEND", "CONTRIBUTION"]
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
                    EventCashflow.user_id == user_id,
                    EventCashflow.simulation_id == simulation_id,
                    EventCashflow.event_date <= snapshot_date,
                )
            ).scalar_one()
        )

        # --------------------------------------------------
        # 2.5. TOTAL CONTRIBUTIONS
        # --------------------------------------------------
        total_contribution = Decimal(
            session.execute(
                select(
                    func.coalesce(
                        func.sum(EventCashflow.amount),
                        0,
                    )
                ).where(
                    EventCashflow.user_id == user_id,
                    EventCashflow.simulation_id == simulation_id,
                    EventCashflow.event_type == "CONTRIBUTION",
                    EventCashflow.event_date <= snapshot_date,
                )
            ).scalar_one()
        )

        # --------------------------------------------------
        # 3. FIXED INCOME (MARK-TO-MARKET)
        # --------------------------------------------------
        total_fixed = Decimal(
            session.execute(
                select(
                    func.coalesce(
                        func.sum(FixedIncomePosition.current_value),
                        0,
                    )
                ).where(
                    FixedIncomePosition.user_id == user_id,
                    FixedIncomePosition.simulation_id == simulation_id,
                )
            ).scalar_one()
        )

        # --------------------------------------------------
        # 4. NET WORTH
        # --------------------------------------------------
        total_networth = total_cash + total_equity + total_fixed

        # --------------------------------------------------
        # 5. Persistir snapshot
        # --------------------------------------------------
        snapshot = Snapshots(
            simulation_id=simulation_id,
            user_id=user_id,
            snapshot_date=snapshot_date,
            total_equity=total_equity,
            total_fixed=total_fixed,
            total_cash=total_cash,
            total_contribution=total_contribution,
            total_networth=total_networth,
            created_at=datetime.now(UTC),
        )

        session.merge(snapshot)

        return SnapshotDTO.from_model(snapshot)

    @transactional
    def get_last_snapshot_date(
        self, session: Session, simulation_id: int
    ) -> date | None:
        """Retorna a última data de snapshot registrada para a simulação"""
        last_date = session.execute(
            select(func.max(Snapshots.snapshot_date)).where(
                Snapshots.simulation_id == simulation_id
            )
        ).scalar_one_or_none()
        return last_date
