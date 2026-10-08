from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.enum import EquityEventType
from backend.core.models.models import (
    EventEquity,
    Snapshots,
    Stock,
)
from backend.core.runtime.simulation_manager import SimulationManager


class PortfolioRepository:
    @transactional
    def get_patrimonial_history(
        self, session: Session, user_id: int
    ) -> list[PatrimonialHistoryDTO]:
        simulation_id = SimulationManager.get_active_simulation_id()
        rows = session.scalars(
            select(Snapshots)
            .where(
                Snapshots.user_id == user_id,
                Snapshots.simulation_id == simulation_id,
            )
            .order_by(Snapshots.snapshot_date)
        ).all()

        return [
            PatrimonialHistoryDTO(
                snapshot_date=row.snapshot_date,
                total_networth=row.total_networth,
                total_equity=row.total_equity,
                total_fixed=row.total_fixed,
                total_cash=row.total_cash,
                total_contribution=row.total_contribution,
            )
            for row in rows
        ]

    @transactional
    def get_equity_events(self, session: Session, user_id: int) -> list[EquityEventDTO]:
        """Eventos de renda variável do jogador, em ordem cronológica."""
        simulation_id = SimulationManager.get_active_simulation_id()
        rows = session.execute(
            select(EventEquity, Stock.ticker)
            .join(Stock, Stock.id == EventEquity.stock_id)
            .where(
                EventEquity.user_id == user_id,
                EventEquity.simulation_id == simulation_id,
            )
            .order_by(EventEquity.event_date, EventEquity.id)
        ).all()

        return [
            EquityEventDTO(
                simulation_id=event.simulation_id,
                user_id=event.user_id,
                event_type=EquityEventType(event.event_type),
                ticker=ticker,
                quantity=event.quantity,
                price=event.price,
                event_date=event.event_date,
                created_at=event.created_at,
            )
            for event, ticker in rows
        ]
