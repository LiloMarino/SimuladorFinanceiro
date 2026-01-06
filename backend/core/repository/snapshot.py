from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Case, func, select, true
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.snapshot import SnapshotDTO
from backend.core.models.models import (
    EventCashflow,
    EventEquity,
    FixedIncomePosition,
    Snapshots,
    StockPriceHistory,
)


class SnapshotRepository:
    @transactional
    def create_snapshot(
        self,
        session: Session,
        user_id: int,
        snapshot_date: date,
    ) -> SnapshotDTO:
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
                    EventCashflow.user_id == user_id,
                    EventCashflow.event_date <= snapshot_date,
                )
            ).scalar_one()
        )

        # --------------------------------------------------
        # 3. EQUITY (MARK-TO-MARKET)
        # --------------------------------------------------
        positions = (
            select(
                EventEquity.stock_id,
                func.sum(
                    Case(
                        (EventEquity.event_type == "BUY", EventEquity.quantity),
                        (EventEquity.event_type == "SELL", -EventEquity.quantity),
                        else_=0,
                    )
                ).label("quantity"),
            )
            .where(
                EventEquity.user_id == user_id,
                EventEquity.event_date <= snapshot_date,
            )
            .group_by(EventEquity.stock_id)
        ).subquery()

        price_lateral = (
            select(StockPriceHistory.close)
            .where(
                StockPriceHistory.stock_id == positions.c.stock_id,
                StockPriceHistory.price_date <= snapshot_date,
            )
            .order_by(StockPriceHistory.price_date.desc())
            .limit(1)
            .lateral()
        )

        total_equity = Decimal(
            session.execute(
                select(
                    func.coalesce(
                        func.sum(positions.c.quantity * price_lateral.c.close),
                        0,
                    )
                )
                .select_from(positions)
                .join(price_lateral, true())
                .where(positions.c.quantity != 0)
            ).scalar_one()
        )

        # --------------------------------------------------
        # 4. FIXED INCOME (MARK-TO-MARKET)
        # --------------------------------------------------
        total_fixed = Decimal(
            session.execute(
                select(
                    func.coalesce(
                        func.sum(FixedIncomePosition.current_value),
                        0,
                    )
                ).where(FixedIncomePosition.user_id == user_id)
            ).scalar_one()
        )

        # --------------------------------------------------
        # 5. NET WORTH
        # --------------------------------------------------
        total_networth = total_cash + total_equity + total_fixed

        # --------------------------------------------------
        # 6. Persistir snapshot
        # --------------------------------------------------
        snapshot = Snapshots(
            user_id=user_id,
            snapshot_date=snapshot_date,
            total_equity=total_equity,
            total_fixed=total_fixed,
            total_cash=total_cash,
            total_networth=total_networth,
            created_at=datetime.now(UTC),
        )

        session.merge(snapshot)

        return SnapshotDTO(
            user_id=user_id,
            snapshot_date=snapshot_date,
            total_equity=total_equity,
            total_fixed=total_fixed,
            total_cash=total_cash,
            total_networth=total_networth,
            created_at=datetime.now(UTC),
        )

    @transactional
    def get_last_snapshot_date(self, session: Session) -> date | None:
        """Retorna a última data de snapshot registrada"""
        last_date = session.execute(
            select(func.max(Snapshots.snapshot_date))
        ).scalar_one_or_none()
        return last_date
