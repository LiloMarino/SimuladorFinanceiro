from datetime import date
from decimal import Decimal
from typing import NamedTuple

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.dividends import DividendPaymentDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.order_preview import TradeDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.enum import AssetClass, CashflowEventType, EquityEventType
from backend.core.models.models import (
    EventCashflow,
    EventEquity,
    SimulationPlayers,
    Snapshots,
    Stock,
    Users,
)
from backend.core.runtime.simulation_manager import SimulationManager


class DividendTotal(NamedTuple):
    """Proventos de um ativo: a partida inteira e a janela pedida."""

    total: Decimal
    recent: Decimal


class PortfolioRepository:
    @transactional
    def get_patrimonial_history(
        self,
        session: Session,
        user_id: int,
        before: date | None = None,
        last: int | None = None,
    ) -> list[PatrimonialHistoryDTO]:
        """Os snapshots em ordem de data; com `last`, só os `last` mais recentes antes de `before`."""
        simulation_id = SimulationManager.get_active_simulation_id()
        stmt = select(Snapshots).where(
            Snapshots.user_id == user_id,
            Snapshots.simulation_id == simulation_id,
        )
        if before is not None:
            stmt = stmt.where(Snapshots.snapshot_date < before)
        if last is None:
            rows = session.scalars(stmt.order_by(Snapshots.snapshot_date)).all()
        else:
            recent = stmt.order_by(Snapshots.snapshot_date.desc()).limit(last)
            rows = list(reversed(session.scalars(recent).all()))

        return [
            PatrimonialHistoryDTO(
                snapshot_date=row.snapshot_date,
                total_networth=row.total_networth,
                total_equity=row.total_equity,
                total_fixed=row.total_fixed,
                total_cash=row.total_cash,
                total_contribution=row.total_contribution,
                total_debt=row.total_debt,
                equity_by_class=row.equity_by_class,
            )
            for row in rows
        ]

    @transactional
    def get_trades(self, session: Session, ticker: str, limit: int) -> list[TradeDTO]:
        """As últimas execuções de todos os jogadores da partida em `ticker`."""
        simulation_id = SimulationManager.get_active_simulation_id()
        rows = session.execute(
            select(EventEquity, Users.nickname, SimulationPlayers.color)
            .join(Stock, Stock.id == EventEquity.stock_id)
            .join(Users, Users.id == EventEquity.user_id)
            .join(
                SimulationPlayers,
                (SimulationPlayers.simulation_id == EventEquity.simulation_id)
                & (SimulationPlayers.user_id == EventEquity.user_id),
            )
            .where(
                Stock.ticker == ticker,
                EventEquity.simulation_id == simulation_id,
                # O desdobramento e a venda da fração não passam pelo book
                EventEquity.event_type.in_(
                    (EquityEventType.BUY.value, EquityEventType.SELL.value)
                ),
            )
            .order_by(EventEquity.event_date.desc(), EventEquity.id.desc())
            .limit(limit)
        ).all()
        return [
            TradeDTO(
                event_date=event.event_date,
                player_nickname=nickname,
                player_color=color,
                action=EquityEventType(event.event_type).value.lower(),
                quantity=event.quantity,
                price=event.price,
            )
            for event, nickname, color in rows
        ]

    @transactional
    def get_dividend_payments(
        self, session: Session, user_id: int
    ) -> list[DividendPaymentDTO]:
        """Os créditos de provento no caixa do jogador, em ordem de data."""
        simulation_id = SimulationManager.get_active_simulation_id()
        rows = session.execute(
            select(EventCashflow, Stock.ticker, Stock.name, Stock.asset_class)
            .join(Stock, Stock.id == EventCashflow.stock_id)
            .where(
                EventCashflow.user_id == user_id,
                EventCashflow.simulation_id == simulation_id,
                EventCashflow.event_type == CashflowEventType.DIVIDEND.value,
            )
            .order_by(EventCashflow.event_date, EventCashflow.id)
        ).all()
        return [
            DividendPaymentDTO(
                ticker=ticker,
                name=name,
                asset_class=AssetClass(asset_class),
                event_date=event.event_date,
                amount=event.amount,
            )
            for event, ticker, name, asset_class in rows
        ]

    @transactional
    def get_dividend_totals(
        self, session: Session, user_id: int, since: date
    ) -> dict[str, DividendTotal]:
        """Quanto cada ativo pagou ao jogador na partida inteira e de `since` em diante."""
        simulation_id = SimulationManager.get_active_simulation_id()
        since_total = func.coalesce(
            func.sum(
                case((EventCashflow.event_date >= since, EventCashflow.amount), else_=0)
            ),
            0,
        )
        rows = session.execute(
            select(Stock.ticker, func.sum(EventCashflow.amount), since_total)
            .join(Stock, Stock.id == EventCashflow.stock_id)
            .where(
                EventCashflow.user_id == user_id,
                EventCashflow.simulation_id == simulation_id,
                EventCashflow.event_type == CashflowEventType.DIVIDEND.value,
            )
            .group_by(Stock.ticker)
        ).all()
        return {
            ticker: DividendTotal(Decimal(total), Decimal(recent))
            for ticker, total, recent in rows
        }

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
