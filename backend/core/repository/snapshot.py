from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.models.models import (
    EventCashflow,
    EventEquity,
    EventFixedIncome,
    Snapshots,
    Users,
)


class SnapshotRepository:
    @transactional
    def create_snapshot(self, session: Session, current_date: datetime) -> None:
        """
        Snapshot(N) = Snapshot(N-1) + Eventos ocorridos após o último snapshot
        """
        snapshot_date: date = current_date.date()

        users = session.execute(select(Users)).scalars().all()
        for user in users:
            # --------------------------------------------------
            # 1. Buscar último snapshot
            # --------------------------------------------------
            last_snapshot = session.execute(
                select(Snapshots)
                .where(Snapshots.user_id == user.id)
                .order_by(Snapshots.snapshot_date.desc())
                .limit(1)
            ).scalar_one_or_none()

            if last_snapshot:
                base_cash = last_snapshot.total_cash
                base_equity = last_snapshot.total_equity
                base_fixed = last_snapshot.total_fixed
                from_date = last_snapshot.snapshot_date
            else:
                base_cash = Decimal("0")
                base_equity = Decimal("0")
                base_fixed = Decimal("0")
                from_date = None

            # --------------------------------------------------
            # 2. CASHFLOW (incremental)
            # --------------------------------------------------
            cash_delta = session.execute(
                select(
                    func.coalesce(
                        func.sum(
                            func.case(
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
                    EventCashflow.event_date <= snapshot_date,
                    *([EventCashflow.event_date > from_date] if from_date else []),
                )
            ).scalar_one()
            total_cash = base_cash + Decimal(cash_delta)

            # --------------------------------------------------
            # 3. EQUITY (incremental)
            # --------------------------------------------------
            equity_delta = session.execute(
                select(
                    func.coalesce(
                        func.sum(
                            func.case(
                                (
                                    EventEquity.event_type == "BUY",
                                    EventEquity.quantity * EventEquity.price,
                                ),
                                (
                                    EventEquity.event_type == "SELL",
                                    -EventEquity.quantity * EventEquity.price,
                                ),
                                else_=Decimal("0"),
                            )
                        ),
                        0,
                    )
                ).where(
                    EventEquity.user_id == user.id,
                    EventEquity.event_date <= snapshot_date,
                    *([EventEquity.event_date > from_date] if from_date else []),
                )
            ).scalar_one()
            total_equity = base_equity + Decimal(equity_delta)

            # --------------------------------------------------
            # 4. FIXED INCOME (incremental)
            # --------------------------------------------------
            fixed_delta = session.execute(
                select(
                    func.coalesce(
                        func.sum(
                            func.case(
                                (
                                    EventFixedIncome.event_type == "BUY",
                                    EventFixedIncome.amount,
                                ),
                                (
                                    EventFixedIncome.event_type == "REDEEM",
                                    -EventFixedIncome.amount,
                                ),
                                else_=Decimal("0"),
                            )
                        ),
                        0,
                    )
                ).where(
                    EventFixedIncome.user_id == user.id,
                    EventFixedIncome.event_date <= snapshot_date,
                    *([EventFixedIncome.event_date > from_date] if from_date else []),
                )
            ).scalar_one()
            total_fixed = base_fixed + Decimal(fixed_delta)

            # --------------------------------------------------
            # 5. NET WORTH
            # --------------------------------------------------
            total_networth = total_cash + total_equity + total_fixed

            # --------------------------------------------------
            # 6. Persistir snapshot
            # --------------------------------------------------
            snapshot = Snapshots(
                user_id=user.id,
                snapshot_date=snapshot_date,
                total_equity=total_equity,
                total_fixed=total_fixed,
                total_cash=total_cash,
                total_networth=total_networth,
                created_at=datetime.now(UTC),
            )
            session.merge(snapshot)
