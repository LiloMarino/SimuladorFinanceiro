from sqlalchemy import Case, func, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.position import PositionDTO
from backend.core.models.models import EventEquity, Stock


class PortfolioRepository:
    @transactional
    def get_portfolio(self, session: Session, client_id: str):
        pass

    @transactional
    def get_equity_positions(self, session: Session, user_id: int) -> list[PositionDTO]:
        rows = session.execute(
            select(
                Stock.ticker.label("ticker"),
                func.sum(
                    Case(
                        (EventEquity.event_type == "BUY", EventEquity.quantity),
                        (EventEquity.event_type == "SELL", -EventEquity.quantity),
                        else_=0,
                    )
                ).label("size"),
                func.sum(
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
                ).label("total_cost"),
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
            )
            for row in rows
            if row.size != 0
        ]

    @transactional
    def get_fixed_income_positions(self, session: Session, client_id: str):
        pass
