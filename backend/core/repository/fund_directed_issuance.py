from datetime import date
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.fund import FundDirectedIssuanceDTO
from backend.core.enum import FundDirectedIssuanceStatus
from backend.core.models.models import FundDirectedIssuances


def _to_dto(row: FundDirectedIssuances) -> FundDirectedIssuanceDTO:
    return FundDirectedIssuanceDTO(
        id=row.id,
        buyer_user_id=row.buyer_user_id,
        quotas=row.quotas,
        offered_on=row.offered_on,
        status=FundDirectedIssuanceStatus(row.status),
        price=row.price,
        settled_on=row.settled_on,
    )


class FundDirectedIssuanceRepository:
    @transactional
    def pending_of_fund(
        self, session: Session, fund_id: int
    ) -> FundDirectedIssuanceDTO | None:
        """A oferta que espera a resposta do co-gestor; a gestora tem no máximo uma."""
        row = session.scalars(
            select(FundDirectedIssuances)
            .where(
                FundDirectedIssuances.fund_id == fund_id,
                FundDirectedIssuances.status
                == FundDirectedIssuanceStatus.OFFERED.value,
            )
            .order_by(FundDirectedIssuances.id.desc())
            .limit(1)
        ).first()
        return _to_dto(row) if row else None

    @transactional
    def settled_of_fund(
        self, session: Session, fund_id: int
    ) -> list[FundDirectedIssuanceDTO]:
        """As emissões dirigidas liquidadas, da mais antiga à mais nova."""
        rows = session.scalars(
            select(FundDirectedIssuances)
            .where(
                FundDirectedIssuances.fund_id == fund_id,
                FundDirectedIssuances.status
                == FundDirectedIssuanceStatus.ACCEPTED.value,
            )
            .order_by(FundDirectedIssuances.id)
        ).all()
        return [_to_dto(row) for row in rows]

    @transactional
    def create(
        self,
        session: Session,
        fund_id: int,
        buyer_user_id: int,
        quotas: Decimal,
        offered_on: date,
        status: FundDirectedIssuanceStatus,
        price: Decimal | None = None,
        settled_on: date | None = None,
    ) -> FundDirectedIssuanceDTO:
        """Grava a emissão dirigida: a oferta ao co-gestor ou a liquidada na hora."""
        row = FundDirectedIssuances(
            fund_id=fund_id,
            buyer_user_id=buyer_user_id,
            quotas=quotas,
            offered_on=offered_on,
            status=status.value,
            price=price,
            settled_on=settled_on,
        )
        session.add(row)
        session.flush()
        return _to_dto(row)

    @transactional
    def close(
        self,
        session: Session,
        issuance_id: int,
        status: FundDirectedIssuanceStatus,
        price: Decimal | None = None,
        settled_on: date | None = None,
    ) -> None:
        """Dá o desfecho da oferta: liquidada (com preço e dia), recusada, vencida ou cancelada."""
        session.execute(
            update(FundDirectedIssuances)
            .where(FundDirectedIssuances.id == issuance_id)
            .values(status=status.value, price=price, settled_on=settled_on)
        )
