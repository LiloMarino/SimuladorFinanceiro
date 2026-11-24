from datetime import date
from decimal import Decimal
from typing import Literal

from sqlalchemy import ColumnElement, and_, delete, func, or_, select, update
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
# A chave de `params` onde a linha de contratação de empréstimo guarda o juro anual do contrato
ANNUAL_RATE = "annual_rate"
# As chaves de `params` do prazo contratado e do número do empréstimo nas linhas de crédito
TERM_MONTHS = "term_months"
LOAN_NUMBER = "loan_number"


def event_dto(row: StrategyLog) -> StrategyEventDTO:
    return StrategyEventDTO(
        simulation_id=row.simulation_id,
        user_id=row.user_id,
        fund_id=row.fund_id,
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


def contract_rate(params: dict | None) -> Decimal | None:
    """O juro do contrato, que a linha de contratação guarda em `params`."""
    rate = params.get(ANNUAL_RATE) if params else None
    return None if rate is None else Decimal(str(rate))


def contract_term(params: dict | None) -> int | None:
    """O prazo em meses que a linha de contratação guarda em `params`."""
    term = params.get(TERM_MONTHS) if params else None
    return None if term is None else int(term)


def loan_number(params: dict | None) -> int | None:
    """O número do empréstimo que a linha de crédito guarda em `params`."""
    number = params.get(LOAN_NUMBER) if params else None
    return None if number is None else int(number)


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
        annual_rate=contract_rate(row.params),
        term_months=contract_term(row.params),
        loan_number=loan_number(row.params),
    )


def log_models(events: list[StrategyEventDTO]) -> list[StrategyLog]:
    return [
        StrategyLog(
            simulation_id=e.simulation_id,
            user_id=e.user_id,
            fund_id=e.fund_id,
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


def owner_clauses(
    user_id: int | None, fund_id: int | None
) -> list[ColumnElement[bool]]:
    """As linhas da gestora `fund_id`; sem ela, as da conta pessoal (de `user_id`, ou de todos)."""
    if fund_id is not None:
        return [StrategyLog.fund_id == fund_id]
    clauses: list[ColumnElement[bool]] = [StrategyLog.fund_id.is_(None)]
    if user_id is not None:
        clauses.append(StrategyLog.user_id == user_id)
    return clauses


def log_where(
    simulation_id: int, user_id: int, kind: LogFilter, fund_id: int | None
) -> list[ColumnElement[bool]]:
    """As linhas do registro do jogador ou da gestora que o filtro `kind` mostra."""
    where = [
        StrategyLog.simulation_id == simulation_id,
        StrategyLog.kind != ERROR_SEEN,
        *owner_clauses(user_id, fund_id),
    ]
    if kind == "orders":
        where.append(StrategyLog.kind == ORDER)
    elif kind == "modes":
        where.append(StrategyLog.kind != ORDER)
    return where


# A ordem do registro: o dia e, no mesmo dia, a linha gravada por último, primeiro
LOG_ORDER = (StrategyLog.event_date.desc(), StrategyLog.id.desc())


class StrategyRepository:
    @transactional
    def mode_rows(
        self,
        session: Session,
        simulation_id: int,
        user_id: int | None = None,
        fund_id: int | None = None,
    ) -> list[StrategyEventDTO]:
        """As linhas de modo (tudo menos ordens) na ordem em que aconteceram."""
        stmt = (
            select(StrategyLog)
            .where(
                StrategyLog.simulation_id == simulation_id,
                StrategyLog.kind != ORDER,
                *owner_clauses(user_id, fund_id),
            )
            .order_by(StrategyLog.id)
        )
        return [event_dto(row) for row in session.scalars(stmt).all()]

    @transactional
    def fund_mode_rows(
        self, session: Session, simulation_id: int
    ) -> list[StrategyEventDTO]:
        """As linhas de modo de todas as gestoras da partida, na ordem em que aconteceram."""
        stmt = (
            select(StrategyLog)
            .where(
                StrategyLog.simulation_id == simulation_id,
                StrategyLog.kind != ORDER,
                StrategyLog.fund_id.is_not(None),
            )
            .order_by(StrategyLog.id)
        )
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
        fund_id: int | None = None,
    ) -> tuple[list[StrategyLogRowDTO], int]:
        """Uma página do registro do jogador ou da gestora, da linha mais recente para a mais antiga."""
        where = log_where(simulation_id, user_id, kind, fund_id)
        total = session.execute(
            select(func.count()).select_from(StrategyLog).where(*where)
        ).scalar_one()
        rows = session.scalars(
            select(StrategyLog)
            .where(*where)
            .order_by(*LOG_ORDER)
            .offset(offset)
            .limit(limit)
        ).all()
        return [row_dto(row) for row in rows], total

    @transactional
    def log_before(
        self,
        session: Session,
        simulation_id: int,
        user_id: int,
        kind: LogFilter,
        before: int | None,
        limit: int,
        fund_id: int | None = None,
    ) -> tuple[list[StrategyLogRowDTO], int]:
        """
        As `limit` linhas do registro mais antigas que a linha `before` (as mais recentes, sem
        ela), na ordem do registro, e o total do filtro. Linha que não está no filtro, ou que
        deixou de existir, não tem linhas antes dela.
        """
        where = log_where(simulation_id, user_id, kind, fund_id)
        total = session.execute(
            select(func.count()).select_from(StrategyLog).where(*where)
        ).scalar_one()
        older: list[ColumnElement[bool]] = []
        if before is not None:
            anchor = session.execute(
                select(StrategyLog.event_date).where(StrategyLog.id == before, *where)
            ).scalar_one_or_none()
            if anchor is None:
                return [], total
            older.append(
                or_(
                    StrategyLog.event_date < anchor,
                    and_(StrategyLog.event_date == anchor, StrategyLog.id < before),
                )
            )
        rows = session.scalars(
            select(StrategyLog).where(*where, *older).order_by(*LOG_ORDER).limit(limit)
        ).all()
        return [row_dto(row) for row in rows], total

    @transactional
    def log_totals(
        self,
        session: Session,
        simulation_id: int,
        user_id: int,
        fund_id: int | None = None,
    ) -> dict[LogFilter, int]:
        """O total de linhas do registro em cada filtro."""
        where = log_where(simulation_id, user_id, "all", fund_id)
        orders = session.execute(
            select(func.count())
            .select_from(StrategyLog)
            .where(*where, StrategyLog.kind == ORDER)
        ).scalar_one()
        everything = session.execute(
            select(func.count()).select_from(StrategyLog).where(*where)
        ).scalar_one()
        return {"all": everything, "orders": orders, "modes": everything - orders}

    @transactional
    def log_row_by_order(
        self, session: Session, simulation_id: int, order_id: str
    ) -> tuple[StrategyLogRowDTO, int, int | None] | None:
        """A linha da ordem, com o jogador e a gestora dona do registro em que ela está."""
        row = session.scalars(
            select(StrategyLog).where(
                StrategyLog.simulation_id == simulation_id,
                StrategyLog.order_id == order_id,
            )
        ).first()
        return None if row is None else (row_dto(row), row.user_id, row.fund_id)

    @transactional
    def order_counts(
        self,
        session: Session,
        simulation_id: int,
        user_id: int,
        since: date,
        fund_id: int | None = None,
    ) -> dict[StrategyOrderStatus, int]:
        """Ordens enviadas desde `since`, por situação; o cancelamento em si não conta."""
        rows = session.execute(
            select(StrategyLog.status, func.count())
            .where(
                StrategyLog.simulation_id == simulation_id,
                StrategyLog.kind == ORDER,
                StrategyLog.action != StrategyAction.CANCEL.value,
                *owner_clauses(user_id, fund_id),
                StrategyLog.event_date >= since,
            )
            .group_by(StrategyLog.status)
        ).all()
        return {StrategyOrderStatus(status): count for status, count in rows if status}

    @transactional
    def last_order(
        self,
        session: Session,
        simulation_id: int,
        user_id: int,
        fund_id: int | None = None,
    ) -> StrategyEventDTO | None:
        row = session.scalars(
            select(StrategyLog)
            .where(
                StrategyLog.simulation_id == simulation_id,
                StrategyLog.kind == ORDER,
                *owner_clauses(user_id, fund_id),
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
