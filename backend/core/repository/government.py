from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.government import GovernmentStateDTO
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.models.models import (
    EventCashflow,
    EventFixedIncome,
    GovernmentEvent,
    Simulations,
)


class GovernmentRepository:
    def __init__(self):
        self._states: dict[int, list[GovernmentStateDTO]] = {}
        self._enabled: set[int] = set()

    def clear_cache(self):
        self._states = {}
        self._enabled = set()

    @transactional
    def collected_taxes(
        self, session: Session, simulation_id: int, on: date
    ) -> Decimal:
        variable = Decimal(
            session.scalar(
                select(func.coalesce(func.sum(EventCashflow.amount), 0)).where(
                    EventCashflow.simulation_id == simulation_id,
                    EventCashflow.event_type == "TAX",
                    EventCashflow.event_date <= on,
                )
            )
            or 0
        )
        fixed = session.scalar(
            select(func.coalesce(func.sum(EventFixedIncome.withheld_tax), 0)).where(
                EventFixedIncome.simulation_id == simulation_id,
                EventFixedIncome.event_date <= on,
            )
        ) or Decimal(0)
        return variable + fixed

    @transactional
    def has_request(
        self, session: Session, simulation_id: int, request_key: str
    ) -> bool:
        return (
            session.scalar(
                select(GovernmentEvent.id)
                .where(
                    GovernmentEvent.simulation_id == simulation_id,
                    GovernmentEvent.request_key == request_key,
                )
                .limit(1)
            )
            is not None
        )

    def states(self, simulation_id: int) -> list[GovernmentStateDTO]:
        self._enabled.add(simulation_id)
        if simulation_id not in self._states:
            self._states = {**self._states, simulation_id: self._load(simulation_id)}
        return self._states[simulation_id]

    @transactional
    def _load(self, session: Session, simulation_id: int) -> list[GovernmentStateDTO]:
        return [
            GovernmentStateDTO.model_validate(row)
            for row in session.scalars(
                select(GovernmentEvent.outcome)
                .where(GovernmentEvent.simulation_id == simulation_id)
                .order_by(GovernmentEvent.revision)
            ).all()
        ]

    def append(
        self,
        simulation_id: int,
        state: GovernmentStateDTO,
        kind: str,
        actor: int | None,
        debits: dict[int, Decimal],
        request_key: str | None = None,
    ) -> None:
        previous = self.states(simulation_id)
        self._append(simulation_id, state, kind, actor, debits, request_key)
        # Só publica o resultado em memória depois do commit; erro não muda o estado vivo.
        self._states = {**self._states, simulation_id: [*previous, state]}

    @transactional
    def _append(
        self,
        session: Session,
        simulation_id: int,
        state: GovernmentStateDTO,
        kind: str,
        actor: int | None,
        debits: dict[int, Decimal],
        request_key: str | None = None,
    ) -> None:
        session.execute(
            select(Simulations.id)
            .where(Simulations.id == simulation_id)
            .with_for_update()
        ).scalar_one()
        previous = (
            session.scalar(
                select(GovernmentEvent.revision)
                .where(GovernmentEvent.simulation_id == simulation_id)
                .order_by(GovernmentEvent.revision.desc())
                .limit(1)
            )
            or 0
        )
        if state.revision != previous + 1:
            raise ConflictError(
                "O governo foi atualizado. Atualize a tela antes de tentar novamente."
            )
        session.add(
            GovernmentEvent(
                simulation_id=simulation_id,
                revision=state.revision,
                event_date=state.processed_on,
                kind=kind,
                request_key=request_key,
                actor=actor,
                outcome=state.model_dump(mode="json"),
            )
        )
        for user_id, amount in debits.items():
            if amount > 0:
                session.add(
                    EventCashflow(
                        simulation_id=simulation_id,
                        user_id=user_id,
                        event_type="CAMPAIGN",
                        amount=amount,
                        event_date=state.processed_on,
                        created_at=datetime.now(UTC),
                    )
                )
