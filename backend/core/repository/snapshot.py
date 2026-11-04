from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func, insert, select
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.snapshot import DayBalanceDTO, SnapshotDTO
from backend.core.enum import CONTRIBUTION_TYPES, AssetClass
from backend.core.models.models import (
    EventCashflow,
    Snapshots,
)
from backend.core.repository.cashflow import cash_delta
from backend.core.runtime.simulation_manager import SimulationManager


class SnapshotRepository:
    def create_snapshot(
        self,
        user_id: int,
        snapshot_date: date,
        total_equity: Decimal,
        total_fixed: Decimal,
        total_debt: Decimal,
        equity_by_class: dict[AssetClass, Decimal] | None = None,
    ) -> SnapshotDTO:
        """O snapshot de um jogador só, pelo mesmo caminho do dia de todos."""
        balance = DayBalanceDTO(total_equity, total_fixed, total_debt, equity_by_class)
        return self.create_snapshots(snapshot_date, {user_id: balance})[user_id]

    @transactional
    def create_snapshots(
        self, session: Session, snapshot_date: date, balances: dict[int, DayBalanceDTO]
    ) -> dict[int, SnapshotDTO]:
        """
        Grava o snapshot do dia de cada `user_id` numa ida ao banco para ler e outra
        para gravar. As ações e a renda fixa vêm do motor: as ações ao preço negociado
        na simulação, que difere do histórico quando o impacto de preço está ligado, e
        a renda fixa com o rendimento do dia já acumulado. A dívida é o saldo devedor
        do dia: o patrimônio é o que o jogador tem menos o que deve. O caixa e o aporte
        são a soma dos eventos de caixa até o dia.
        """
        simulation_id = SimulationManager.get_active_simulation_id()
        cashflow = {
            user_id: (Decimal(cash), Decimal(contribution))
            for user_id, cash, contribution in session.execute(
                select(
                    EventCashflow.user_id,
                    cash_delta(),
                    cash_delta(CONTRIBUTION_TYPES),
                )
                .where(
                    EventCashflow.user_id.in_(balances),
                    EventCashflow.simulation_id == simulation_id,
                    EventCashflow.event_date <= snapshot_date,
                )
                .group_by(EventCashflow.user_id)
            ).all()
        }

        created_at = datetime.now(UTC)
        snapshots: dict[int, SnapshotDTO] = {}
        for user_id, balance in balances.items():
            cash, contribution = cashflow.get(user_id, (Decimal(0), Decimal(0)))
            snapshots[user_id] = SnapshotDTO(
                user_id=user_id,
                snapshot_date=snapshot_date,
                total_equity=balance.total_equity,
                total_fixed=balance.total_fixed,
                total_cash=cash,
                total_debt=balance.total_debt,
                total_contribution=contribution,
                total_networth=cash
                + balance.total_equity
                + balance.total_fixed
                - balance.total_debt,
                equity_by_class=balance.equity_by_class,
                created_at=created_at,
            )
        if not snapshots:
            return snapshots

        stmt = upsert(Snapshots).values(
            [
                {"simulation_id": simulation_id, **snapshot.model_dump()}
                for snapshot in snapshots.values()
            ]
        )
        session.execute(
            stmt.on_conflict_do_update(
                index_elements=["simulation_id", "user_id", "snapshot_date"],
                set_={
                    column: stmt.excluded[column]
                    for column in SnapshotDTO.model_fields
                    if column not in ("user_id", "snapshot_date")
                },
            )
        )
        return snapshots

    @transactional
    def create_many(
        self, session: Session, simulation_id: int, snapshots: list[SnapshotDTO]
    ) -> None:
        """Grava os snapshots já calculados numa transação só (o backtest grava em lote)."""
        if not snapshots:
            return
        session.execute(
            insert(Snapshots).values(
                [
                    {
                        "simulation_id": simulation_id,
                        **snapshot.model_dump(),
                    }
                    for snapshot in snapshots
                ]
            )
        )

    @transactional
    def contributions(
        self, session: Session, simulation_id: int
    ) -> list[tuple[date, Decimal]]:
        """O aporte acumulado até cada pregão gravado; é igual para todos os jogadores da partida."""
        rows = session.execute(
            select(Snapshots.snapshot_date, func.max(Snapshots.total_contribution))
            .where(Snapshots.simulation_id == simulation_id)
            .group_by(Snapshots.snapshot_date)
            .order_by(Snapshots.snapshot_date)
        ).all()
        return [(day, total) for day, total in rows]

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
