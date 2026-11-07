from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.corporate_event import CorporateEventDTO
from backend.core.enum import DataOrigin
from backend.core.models.models import StockCorporateEvent
from backend.core.repository.series_version import (
    COMMON_VERSION,
    reading_version,
    seen_by,
)


class CorporateEventRepository:
    @transactional
    def replace_real(
        self,
        session: Session,
        stock_id: int,
        events: Sequence[CorporateEventDTO],
        since: date,
    ) -> None:
        """
        Troca os eventos reais comuns do ativo de `since` em diante pelos que
        chegaram: a fonte devolve o histórico inteiro a cada importação.
        """
        session.execute(
            delete(StockCorporateEvent).where(
                StockCorporateEvent.stock_id == stock_id,
                StockCorporateEvent.version == COMMON_VERSION,
                StockCorporateEvent.origin == DataOrigin.REAL.value,
                StockCorporateEvent.ex_date >= since,
            )
        )
        session.add_all(
            StockCorporateEvent(
                stock_id=stock_id,
                ex_date=event.ex_date,
                kind=event.kind.value,
                value=Decimal(str(event.value)),
                origin=DataOrigin.REAL.value,
            )
            for event in events
        )

    @transactional
    def get_between(
        self,
        session: Session,
        after: date,
        until: date,
        simulation_id: int | None = None,
    ) -> list[CorporateEventDTO]:
        """Os eventos com data ex em (`after`, `until`], de todos os ativos, por data."""
        rows = (
            session.execute(
                select(StockCorporateEvent)
                .where(
                    StockCorporateEvent.ex_date > after,
                    StockCorporateEvent.ex_date <= until,
                    seen_by(StockCorporateEvent, reading_version(simulation_id)),
                )
                .order_by(StockCorporateEvent.ex_date, StockCorporateEvent.stock_id)
            )
            .scalars()
            .all()
        )
        return [CorporateEventDTO.from_model(row) for row in rows]

    @transactional
    def get_real(self, session: Session) -> list[CorporateEventDTO]:
        """Todos os eventos reais da série comum, por ativo e data."""
        rows = (
            session.execute(
                select(StockCorporateEvent)
                .where(
                    StockCorporateEvent.version == COMMON_VERSION,
                    StockCorporateEvent.origin == DataOrigin.REAL.value,
                )
                .order_by(StockCorporateEvent.stock_id, StockCorporateEvent.ex_date)
            )
            .scalars()
            .all()
        )
        return [CorporateEventDTO.from_model(row) for row in rows]
