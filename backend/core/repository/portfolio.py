from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from sqlalchemy import Case, func, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.fixed_income_position import FixedIncomePositionDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.position import PositionDTO
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.core.models.models import (
    EventEquity,
    EventFixedIncome,
    FixedIncomeAsset,
    Snapshots,
    Stock,
)


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
                total_cost=float(row.total_cost),
                avg_price=float(row.avg_price),
            )
            for row in rows
            if row.size != 0
        ]

    @transactional
    def get_fixed_income_positions(
        self, session: Session, user_id: int
    ) -> list[FixedIncomePositionDTO]:
        # Subquery para somar BUYs e subtrair REDEEMs
        total_applied_subq = (
            select(
                EventFixedIncome.asset_id,
                func.sum(
                    Case(
                        (EventFixedIncome.event_type == "BUY", EventFixedIncome.amount),
                        (
                            EventFixedIncome.event_type == "REDEEM",
                            -EventFixedIncome.amount,
                        ),
                        else_=0,
                    )
                ).label("total_applied"),
                func.min(
                    Case(
                        (
                            EventFixedIncome.event_type == "BUY",
                            EventFixedIncome.event_date,
                        )
                    )
                ).label("first_applied_date"),  # Data do primeiro aporte
            )
            .where(EventFixedIncome.user_id == user_id)
            .group_by(EventFixedIncome.asset_id)
            .subquery()
        )

        assets = session.scalars(
            select(FixedIncomeAsset)
            .join(
                total_applied_subq,
                total_applied_subq.c.asset_id == FixedIncomeAsset.id,
            )
            .where(total_applied_subq.c.total_applied > 0)
        ).all()

        # Converter totals para dict usando asset_id como chave
        totals_seq: Sequence[tuple[int, Decimal, date]] = (
            session.execute(
                select(
                    total_applied_subq.c.asset_id,
                    total_applied_subq.c.total_applied,
                    total_applied_subq.c.first_applied_date,
                )
            )
            .tuples()
            .all()
        )
        totals: dict[int, tuple[Decimal, date]] = {
            asset_id: (total_applied, first_applied_date)
            for asset_id, total_applied, first_applied_date in totals_seq
        }

        return [
            FixedIncomePositionDTO(
                asset=FixedIncomeAssetDTO(
                    asset_uuid=asset.asset_uuid,
                    name=asset.name,
                    issuer=asset.issuer,
                    investment_type=FixedIncomeType.from_db(asset.investment_type),
                    rate_index=RateIndexType.from_db(asset.rate_type),
                    maturity_date=asset.maturity_date,
                    interest_rate=float(asset.interest_rate),
                ),
                total_applied=float(totals[asset.id][0]),
                current_value=float(totals[asset.id][0]),
                first_applied_date=totals[asset.id][1],
            )
            for asset in assets
        ]
