from collections import defaultdict
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.events.credit import CreditEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.enum import CashflowEventType, EquityEventType
from backend.core.models.models import (
    EventCashflow,
    EventCredit,
    EventEquity,
    SimulationPlayers,
    Simulations,
    Snapshots,
    Stock,
    Users,
)
from backend.core.repository.credit import credit_event_dto
from backend.core.repository.simulation import decode_settings

# Jogador numa simulação: o nickname é único entre os usuários
type PlayerKey = tuple[int, str]


class StatisticsRepository:
    @transactional
    def get_players_history(
        self, session: Session, simulation_ids: list[int]
    ) -> list[PlayerHistoryDTO]:
        # Capital inicial vem da linha da simulação (nunca do formulário),
        # garantindo métricas consistentes ao continuar/carregar simulações.
        players = session.execute(
            select(
                SimulationPlayers.simulation_id,
                SimulationPlayers.user_id,
                SimulationPlayers.color,
                SimulationPlayers.team,
                Users.nickname,
                Users.is_bot,
                Simulations.name,
                Simulations.rules,
            )
            .join(Users, Users.id == SimulationPlayers.user_id)
            .join(Simulations, Simulations.id == SimulationPlayers.simulation_id)
            .where(SimulationPlayers.simulation_id.in_(simulation_ids))
        ).all()
        snapshots = session.execute(
            select(
                Snapshots.simulation_id,
                Snapshots.user_id,
                Snapshots.snapshot_date,
                Snapshots.total_equity,
                Snapshots.total_fixed,
                Snapshots.total_cash,
                Snapshots.total_networth,
                Snapshots.total_contribution,
                Snapshots.total_debt,
            )
            .where(Snapshots.simulation_id.in_(simulation_ids))
            .order_by(
                Snapshots.simulation_id, Snapshots.user_id, Snapshots.snapshot_date
            )
        ).all()

        # Agrupa os snapshots por jogador em cada simulação, preservando a ordem de data
        grouped: dict[tuple[int, int], list[PatrimonialHistoryDTO]] = defaultdict(list)
        for row in snapshots:
            grouped[(row.simulation_id, row.user_id)].append(
                PatrimonialHistoryDTO(
                    snapshot_date=row.snapshot_date,
                    total_equity=row.total_equity,
                    total_fixed=row.total_fixed,
                    total_cash=row.total_cash,
                    total_networth=row.total_networth,
                    total_contribution=row.total_contribution,
                    total_debt=row.total_debt,
                )
            )

        info = {(p.simulation_id, p.user_id): p for p in players}
        settings = {p.simulation_id: decode_settings(p.name, p.rules) for p in players}
        return [
            PlayerHistoryDTO(
                player_nickname=info[key].nickname,
                color=info[key].color,
                team=info[key].team,
                is_bot=info[key].is_bot,
                simulation_id=key[0],
                simulation_name=info[key].name,
                starting_cash=settings[key[0]].starting_cash,
                goal_net_worth=settings[key[0]].goal_net_worth,
                history=history,
            )
            for key, history in grouped.items()
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
    def get_players_unexpected(
        self, session: Session, simulation_ids: list[int]
    ) -> dict[PlayerKey, dict[str, int]]:
        """Quantos imprevistos de cada tipo (chave do evento) cada jogador sofreu."""
        rows = session.execute(
            select(
                EventCashflow.simulation_id,
                Users.nickname,
                EventCashflow.life_event_key,
                func.count(),
            )
            .join(Users, Users.id == EventCashflow.user_id)
            .where(
                EventCashflow.simulation_id.in_(simulation_ids),
                EventCashflow.event_type == CashflowEventType.UNEXPECTED_EXPENSE.value,
            )
            .group_by(
                EventCashflow.simulation_id,
                Users.nickname,
                EventCashflow.life_event_key,
            )
        ).all()
        counts: dict[PlayerKey, dict[str, int]] = defaultdict(dict)
        for simulation_id, nickname, key, total in rows:
            counts[(simulation_id, nickname)][key or ""] = total
        return counts

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

    @transactional
    def get_players_credit(
        self, session: Session, simulation_ids: list[int]
    ) -> dict[PlayerKey, list[CreditEventDTO]]:
        """Os eventos de crédito de cada jogador, na ordem em que aconteceram."""
        rows = session.execute(
            select(EventCredit, Users.nickname)
            .join(Users, Users.id == EventCredit.user_id)
            .where(EventCredit.simulation_id.in_(simulation_ids))
            .order_by(EventCredit.id)
        ).all()
        events: dict[PlayerKey, list[CreditEventDTO]] = defaultdict(list)
        for row, nickname in rows:
            events[(row.simulation_id, nickname)].append(credit_event_dto(row))
        return events
