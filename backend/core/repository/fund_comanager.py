from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.fund import FundComanagerDTO, FundComanagerEventDTO
from backend.core.enum import FundComanagerStatus
from backend.core.models.models import FundComanagerEvents, FundComanagers

# As colunas que identificam a linha e não mudam no upsert
_KEY = ("fund_id", "user_id")


def _to_dto(row: FundComanagers) -> FundComanagerDTO:
    return FundComanagerDTO(
        user_id=row.user_id,
        status=FundComanagerStatus(row.status),
        share=row.share,
        pending_share=row.pending_share,
        pending_from=row.pending_from,
        invited_on=row.invited_on,
        since=row.since,
    )


class FundComanagerRepository:
    @transactional
    def of_fund(self, session: Session, fund_id: int) -> list[FundComanagerDTO]:
        """Os co-gestores da gestora, dos convites e entradas mais antigos aos mais novos."""
        rows = session.scalars(
            select(FundComanagers)
            .where(FundComanagers.fund_id == fund_id)
            .order_by(FundComanagers.invited_on, FundComanagers.user_id)
        ).all()
        return [_to_dto(row) for row in rows]

    @transactional
    def save(self, session: Session, fund_id: int, comanager: FundComanagerDTO) -> None:
        """Grava o convite novo ou o que muda no co-gestor: estado, parte e parte agendada."""
        values = {
            "fund_id": fund_id,
            **comanager.model_dump(),
            "status": comanager.status.value,
        }
        statement = insert(FundComanagers).values(values)
        session.execute(
            statement.on_conflict_do_update(
                index_elements=["fund_id", "user_id"],
                set_={k: statement.excluded[k] for k in values if k not in _KEY},
            )
        )

    @transactional
    def delete(self, session: Session, fund_id: int, user_id: int) -> None:
        """Tira o co-gestor ou o convite da gestora."""
        session.execute(
            delete(FundComanagers).where(
                FundComanagers.fund_id == fund_id,
                FundComanagers.user_id == user_id,
            )
        )

    @transactional
    def record_event(
        self, session: Session, fund_id: int, event: FundComanagerEventDTO
    ) -> None:
        """Anota a entrada ou a saída de um co-gestor."""
        session.add(FundComanagerEvents(fund_id=fund_id, **event.model_dump()))

    @transactional
    def events(self, session: Session, fund_id: int) -> list[FundComanagerEventDTO]:
        """As entradas e saídas da gestora, da mais antiga à mais nova."""
        rows = session.scalars(
            select(FundComanagerEvents)
            .where(FundComanagerEvents.fund_id == fund_id)
            .order_by(FundComanagerEvents.id)
        ).all()
        return [
            FundComanagerEventDTO(
                user_id=row.user_id,
                kind="joined" if row.kind == "joined" else "left",
                day=row.day,
                share=row.share,
            )
            for row in rows
        ]
