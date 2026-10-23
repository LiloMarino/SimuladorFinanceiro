from datetime import date
from typing import Literal

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.events.strategy import StrategyEventDTO
from backend.core.dto.strategy import StrategyLogRowDTO
from backend.core.enum import (
    StrategyAction,
    StrategyLogKind,
    StrategyOrderStatus,
)
from backend.core.models.models import StrategyLog

type LogFilter = Literal["all", "orders", "modes"]

ORDER = StrategyLogKind.ORDER.value
ERROR_SEEN = StrategyLogKind.ERROR_SEEN.value


def event_dto(row: StrategyLog) -> StrategyEventDTO:
    return StrategyEventDTO(
        simulation_id=row.simulation_id,
        user_id=row.user_id,
        event_date=row.event_date,
        created_at=row.created_at,
        kind=StrategyLogKind(row.kind),
        strategy_key=row.strategy_key,
        params=row.params,
        action=StrategyAction(row.action) if row.action else None,
        ticker=row.ticker,
        asset_uuid=row.asset_uuid,
        asset_name=row.asset_name,
        quantity=row.quantity,
        price=row.price,
        order_type=row.order_type,
        order_id=row.order_id,
        reason=row.reason,
        status=StrategyOrderStatus(row.status) if row.status else None,
        detail=row.detail,
    )


def row_dto(row: StrategyLog) -> StrategyLogRowDTO:
    return StrategyLogRowDTO(
        id=row.id,
        event_date=row.event_date,
        kind=StrategyLogKind(row.kind),
        strategy_key=row.strategy_key,
        strategy_name=None,
        action=StrategyAction(row.action) if row.action else None,
        ticker=row.ticker,
        asset_name=row.asset_name,
        quantity=row.quantity,
        price=row.price,
        order_type=row.order_type,
        reason=row.reason,
        status=StrategyOrderStatus(row.status) if row.status else None,
        # O rastro do erro fica na faixa de erro; na tabela só a causa da recusa
        detail=row.detail if row.kind == ORDER else None,
    )


def log_models(events: list[StrategyEventDTO]) -> list[StrategyLog]:
    return [
        StrategyLog(
            simulation_id=e.simulation_id,
            user_id=e.user_id,
            event_date=e.event_date,
            created_at=e.created_at,
            kind=e.kind.value,
            strategy_key=e.strategy_key,
            params=e.params,
            action=e.action.value if e.action else None,
            ticker=e.ticker,
            asset_uuid=e.asset_uuid,
            asset_name=e.asset_name,
            quantity=e.quantity,
            price=e.price,
            order_type=e.order_type,
            order_id=e.order_id,
            reason=e.reason,
            status=e.status.value if e.status else None,
            detail=e.detail,
        )
        for e in events
    ]


class StrategyRepository:
    @transactional
    def mode_rows(
        self, session: Session, simulation_id: int, user_id: int | None = None
    ) -> list[StrategyEventDTO]:
        """As linhas de modo (tudo menos ordens) na ordem em que aconteceram."""
        stmt = (
            select(StrategyLog)
            .where(
                StrategyLog.simulation_id == simulation_id, StrategyLog.kind != ORDER
            )
            .order_by(StrategyLog.id)
        )
        if user_id is not None:
            stmt = stmt.where(StrategyLog.user_id == user_id)
        return [event_dto(row) for row in session.scalars(stmt).all()]

    @transactional
    def log_page(
        self,
        session: Session,
        simulation_id: int,
        user_id: int,
        kind: LogFilter,
        offset: int,
        limit: int,
    ) -> tuple[list[StrategyLogRowDTO], int]:
        """Uma página do registro do jogador, da linha mais recente para a mais antiga."""
        where = [
            StrategyLog.simulation_id == simulation_id,
            StrategyLog.user_id == user_id,
            StrategyLog.kind != ERROR_SEEN,
        ]
        if kind == "orders":
            where.append(StrategyLog.kind == ORDER)
        elif kind == "modes":
            where.append(StrategyLog.kind != ORDER)
        total = session.execute(
            select(func.count()).select_from(StrategyLog).where(*where)
        ).scalar_one()
        rows = session.scalars(
            select(StrategyLog)
            .where(*where)
            .order_by(StrategyLog.event_date.desc(), StrategyLog.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()
        return [row_dto(row) for row in rows], total

    @transactional
    def order_counts(
        self, session: Session, simulation_id: int, user_id: int, since: date
    ) -> dict[StrategyOrderStatus, int]:
        """Ordens enviadas desde `since`, por situação; o cancelamento em si não conta."""
        rows = session.execute(
            select(StrategyLog.status, func.count())
            .where(
                StrategyLog.simulation_id == simulation_id,
                StrategyLog.user_id == user_id,
                StrategyLog.kind == ORDER,
                StrategyLog.action != StrategyAction.CANCEL.value,
                StrategyLog.event_date >= since,
            )
            .group_by(StrategyLog.status)
        ).all()
        return {StrategyOrderStatus(status): count for status, count in rows if status}

    @transactional
    def last_order(
        self, session: Session, simulation_id: int, user_id: int
    ) -> StrategyEventDTO | None:
        row = session.scalars(
            select(StrategyLog)
            .where(
                StrategyLog.simulation_id == simulation_id,
                StrategyLog.user_id == user_id,
                StrategyLog.kind == ORDER,
            )
            .order_by(StrategyLog.event_date.desc(), StrategyLog.id.desc())
            .limit(1)
        ).first()
        return event_dto(row) if row else None

    @transactional
    def set_order_status(
        self,
        session: Session,
        simulation_id: int,
        order_id: str,
        status: StrategyOrderStatus,
    ) -> None:
        """A situação da ordem é a única coisa que muda numa linha já gravada."""
        session.execute(
            update(StrategyLog)
            .where(
                StrategyLog.simulation_id == simulation_id,
                StrategyLog.order_id == order_id,
            )
            .values(status=status.value)
        )

    @transactional
    def rewind(self, session: Session, simulation_id: int, resume_from: date) -> None:
        """
        Prepara a retomada: o registro volta ao último dia processado, e a ordem
        limitada que ficou aberta ou parcial foi cancelada com a parada.
        """
        session.execute(
            delete(StrategyLog).where(
                StrategyLog.simulation_id == simulation_id,
                StrategyLog.event_date > resume_from,
            )
        )
        session.execute(
            update(StrategyLog)
            .where(
                StrategyLog.simulation_id == simulation_id,
                StrategyLog.kind == ORDER,
                StrategyLog.order_type == "limit",
                StrategyLog.status.in_(
                    [StrategyOrderStatus.OPEN.value, StrategyOrderStatus.PARTIAL.value]
                ),
            )
            .values(status=StrategyOrderStatus.CANCELED.value)
        )
