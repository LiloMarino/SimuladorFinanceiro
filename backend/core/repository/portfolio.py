from sqlalchemy import Case, func, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.position import PositionDTO
from backend.core.models.models import EventEquity, Snapshots, Stock


class PortfolioRepository:
    @transactional
    def get_patrimonial_history(
        self, session: Session, user_id: int
    ) -> list[PatrimonialHistoryDTO]:
        rows = session.execute(
            select(
                Snapshots.snapshot_date,
                Snapshots.total_networth,
                Snapshots.total_equity,
                Snapshots.total_fixed,
                Snapshots.total_cash,
            )
            .where(Snapshots.user_id == user_id)
            .order_by(Snapshots.snapshot_date)
        )

        return [
            PatrimonialHistoryDTO(
                snapshot_date=row.snapshot_date,
                total_networth=row.total_networth,
                total_equity=row.total_equity,
                total_fixed=row.total_fixed,
                total_cash=row.total_cash,
            )
            for row in rows
        ]

    @transactional
    def get_equity_positions(self, session: Session, user_id: int) -> list[PositionDTO]:
        size_expr = func.sum(
            Case(
                (EventEquity.event_type == "BUY", EventEquity.quantity),
                (EventEquity.event_type == "SELL", -EventEquity.quantity),
                else_=0,
            )
        )

        total_cost_expr = func.sum(
            Case(
                (
                    EventEquity.event_type == "BUY",
                    EventEquity.quantity * EventEquity.price,
                ),
                (
                    EventEquity.event_type == "SELL",
                    -(EventEquity.quantity * EventEquity.price),
                ),
                else_=0,
            )
        )

        rows = session.execute(
            select(
                Stock.ticker.label("ticker"),
                size_expr.label("size"),
                total_cost_expr.label("total_cost"),
                (total_cost_expr / func.nullif(size_expr, 0)).label("avg_price"),
            )
            .join(Stock, Stock.id == EventEquity.stock_id)
            .where(EventEquity.user_id == user_id)
            .group_by(Stock.ticker)
        )

        return [
            PositionDTO(
                ticker=row.ticker,
                size=row.size,
                total_cost=row.total_cost,
                avg_price=row.avg_price,
            )
            for row in rows
            if row.size != 0
        ]

    @transactional
    def get_fixed_income_positions(self, session: Session, client_id: str):
        pass
