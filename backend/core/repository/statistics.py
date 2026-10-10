from collections import defaultdict
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.enum import CashflowEventType, EquityEventType
from backend.core.models.models import (
    EventCashflow,
    EventEquity,
    Simulations,
    Snapshots,
    Stock,
    Users,
)

# Jogador numa simulação: o nickname é único entre os usuários
type PlayerKey = tuple[int, str]


class StatisticsRepository:
    @transactional
    def get_players_history(
        self, session: Session, simulation_ids: list[int]
    ) -> list[PlayerHistoryDTO]:
        # Capital inicial vem da linha da simulação (nunca do formulário),
        # garantindo métricas consistentes ao continuar/carregar simulações.
        rows = session.execute(
            select(
                Snapshots, Users.nickname, Simulations.name, Simulations.starting_cash
            )
            .join(Users, Users.id == Snapshots.user_id)
            .join(Simulations, Simulations.id == Snapshots.simulation_id)
            .where(Snapshots.simulation_id.in_(simulation_ids))
            .order_by(
                Snapshots.simulation_id, Snapshots.user_id, Snapshots.snapshot_date
            )
        ).all()

        # Agrupa os snapshots por jogador em cada simulação, preservando a ordem de data
        grouped: dict[tuple[int, int], list] = defaultdict(list)
        for row in rows:
            grouped[(row.Snapshots.simulation_id, row.Snapshots.user_id)].append(row)

        return [
            PlayerHistoryDTO(
                player_nickname=group[0].nickname,
                simulation_id=simulation_id,
                simulation_name=group[0].name,
                starting_cash=group[0].starting_cash,
                history=[
                    PatrimonialHistoryDTO(
                        snapshot_date=r.Snapshots.snapshot_date,
                        total_equity=r.Snapshots.total_equity,
                        total_fixed=r.Snapshots.total_fixed,
                        total_cash=r.Snapshots.total_cash,
                        total_networth=r.Snapshots.total_networth,
                        total_contribution=r.Snapshots.total_contribution,
                    )
                    for r in group
                ],
            )
            for (simulation_id, _), group in grouped.items()
        ]

    @transactional
    def get_players_trades(
        self, session: Session, simulation_ids: list[int]
    ) -> dict[PlayerKey, list[EquityEventDTO]]:
        """Execuções de renda variável de cada jogador, em ordem de data."""
        rows = session.execute(
            select(EventEquity, Stock.ticker, Users.nickname)
            .join(Stock, Stock.id == EventEquity.stock_id)
            .join(Users, Users.id == EventEquity.user_id)
            .where(EventEquity.simulation_id.in_(simulation_ids))
            .order_by(EventEquity.event_date, EventEquity.id)
        ).all()

        trades: dict[PlayerKey, list[EquityEventDTO]] = defaultdict(list)
        for event, ticker, nickname in rows:
            trades[(event.simulation_id, nickname)].append(
                EquityEventDTO(
                    simulation_id=event.simulation_id,
                    user_id=event.user_id,
                    event_date=event.event_date,
                    created_at=event.created_at,
                    ticker=ticker,
                    event_type=EquityEventType(event.event_type),
                    quantity=event.quantity,
                    price=event.price,
                )
            )
        return trades

    @transactional
    def get_players_tax(
        self, session: Session, simulation_ids: list[int]
    ) -> dict[PlayerKey, Decimal]:
        """IR da renda variável que já saiu do caixa de cada jogador."""
        rows = session.execute(
            select(
                EventCashflow.simulation_id,
                Users.nickname,
                func.sum(EventCashflow.amount),
            )
            .join(Users, Users.id == EventCashflow.user_id)
            .where(
                EventCashflow.simulation_id.in_(simulation_ids),
                EventCashflow.event_type == CashflowEventType.TAX.value,
            )
            .group_by(EventCashflow.simulation_id, Users.nickname)
        ).all()
        return {
            (simulation_id, nickname): total for simulation_id, nickname, total in rows
        }
