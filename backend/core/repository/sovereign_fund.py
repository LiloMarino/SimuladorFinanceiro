import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.sovereign_fund import SovereignFlowDTO, SovereignFundDTO
from backend.core.enum import SovereignFlowKind
from backend.core.models.models import (
    Portfolios,
    SovereignFundFlows,
    SovereignFunds,
)


class SovereignFundRepository:
    @transactional
    def ensure(self, session: Session, simulation_id: int) -> SovereignFundDTO:
        """O fundo da partida: abre a carteira (sem jogador dono) e a conta dele na primeira vez."""
        row = session.get(SovereignFunds, simulation_id)
        if row is None:
            portfolio = Portfolios(
                simulation_id=simulation_id,
                user_id=None,
                created_at=datetime.now(UTC),
                starting_cash=Decimal(0),
            )
            session.add(portfolio)
            session.flush()
            row = SovereignFunds(
                simulation_id=simulation_id,
                portfolio_id=portfolio.id,
                client_id=uuid.uuid4(),
            )
            session.add(row)
        return SovereignFundDTO(portfolio_id=row.portfolio_id, client_id=row.client_id)

    @transactional
    def flows(self, session: Session, simulation_id: int) -> list[SovereignFlowDTO]:
        rows = session.scalars(
            select(SovereignFundFlows)
            .where(SovereignFundFlows.simulation_id == simulation_id)
            .order_by(SovereignFundFlows.id)
        )
        return [
            SovereignFlowDTO(
                day=row.day,
                kind=SovereignFlowKind(row.kind),
                amount=row.amount,
                measure_id=row.measure_id,
            )
            for row in rows
        ]

    @transactional
    def add_flow(
        self,
        session: Session,
        simulation_id: int,
        day: date,
        kind: SovereignFlowKind,
        amount: Decimal,
        measure_id: int | None = None,
    ) -> bool:
        """Grava o movimento; False quando o aporte dessa medida já estava gravado."""
        values = {
            "simulation_id": simulation_id,
            "day": day,
            "kind": kind.value,
            "amount": amount,
            "measure_id": measure_id,
        }
        if measure_id is None:
            session.execute(insert(SovereignFundFlows).values(**values))
            return True
        result = session.execute(
            pg_insert(SovereignFundFlows)
            .values(**values)
            .on_conflict_do_nothing(constraint="sovereign_fund_flows_measure_key")
            .returning(SovereignFundFlows.measure_id)
        )
        return result.first() is not None
