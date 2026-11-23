from datetime import date

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.house_report import HouseRecommendationDTO
from backend.core.enum import HouseResult
from backend.core.house_report import Draft, Verdict
from backend.core.models.models import HouseRecommendations


class HouseReportRepository:
    @transactional
    def insert_report(
        self,
        session: Session,
        simulation_id: int,
        month: date,
        issued_on: date,
        drafts: list[Draft],
    ) -> list[HouseRecommendationDTO]:
        """Guarda o relatório do mês como saiu; ele nunca é recalculado."""
        rows = [
            HouseRecommendations(
                simulation_id=simulation_id,
                report_month=month,
                issued_on=issued_on,
                ticker=draft.ticker,
                side=draft.side.value,
                price=draft.price,
                target=draft.target,
                deadline=draft.deadline,
            )
            for draft in drafts
        ]
        session.add_all(rows)
        session.flush()
        return [HouseRecommendationDTO.model_validate(row) for row in rows]

    @transactional
    def months(self, session: Session, simulation_id: int) -> list[date]:
        """Os meses que já têm relatório, do mais recente ao mais antigo."""
        return list(
            session.scalars(
                select(HouseRecommendations.report_month)
                .where(HouseRecommendations.simulation_id == simulation_id)
                .distinct()
                .order_by(HouseRecommendations.report_month.desc())
            )
        )

    @transactional
    def of_month(
        self, session: Session, simulation_id: int, month: date
    ) -> list[HouseRecommendationDTO]:
        """As recomendações do relatório do mês, na ordem em que saíram."""
        rows = session.scalars(
            select(HouseRecommendations)
            .where(
                HouseRecommendations.simulation_id == simulation_id,
                HouseRecommendations.report_month == month,
            )
            .order_by(HouseRecommendations.id)
        )
        return [HouseRecommendationDTO.model_validate(row) for row in rows]

    @transactional
    def by_ids(
        self, session: Session, ids: list[int]
    ) -> dict[int, HouseRecommendationDTO]:
        """As recomendações pelo id."""
        rows = session.scalars(
            select(HouseRecommendations).where(HouseRecommendations.id.in_(ids))
        )
        return {row.id: HouseRecommendationDTO.model_validate(row) for row in rows}

    @transactional
    def open_before(
        self, session: Session, simulation_id: int, day: date
    ) -> list[HouseRecommendationDTO]:
        """As recomendações sem desfecho que saíram antes de `day`."""
        rows = session.scalars(
            select(HouseRecommendations)
            .where(
                HouseRecommendations.simulation_id == simulation_id,
                HouseRecommendations.result.is_(None),
                HouseRecommendations.issued_on < day,
            )
            .order_by(HouseRecommendations.id)
        )
        return [HouseRecommendationDTO.model_validate(row) for row in rows]

    @transactional
    def resolve(
        self, session: Session, verdicts: dict[int, Verdict], day: date
    ) -> None:
        """Grava o desfecho de cada recomendação, dado no dia `day`."""
        for recommendation_id, verdict in verdicts.items():
            session.execute(
                update(HouseRecommendations)
                .where(HouseRecommendations.id == recommendation_id)
                .values(
                    result=verdict.result.value,
                    result_price=verdict.price,
                    resolved_on=day,
                )
            )

    @transactional
    def scoreboard(self, session: Session, simulation_id: int) -> tuple[int, int]:
        """Quantas recomendações acertaram e quantas já têm desfecho."""
        hits, resolved = session.execute(
            select(
                func.count().filter(
                    HouseRecommendations.result == HouseResult.HIT.value
                ),
                func.count(HouseRecommendations.result),
            ).where(HouseRecommendations.simulation_id == simulation_id)
        ).one()
        return hits, resolved

    @transactional
    def rewind(self, session: Session, simulation_id: int, resume_from: date) -> None:
        """Prepara a retomada: some o relatório que saiu depois do último dia processado, e o desfecho dado depois dele volta a aberto."""
        session.execute(
            delete(HouseRecommendations).where(
                HouseRecommendations.simulation_id == simulation_id,
                HouseRecommendations.issued_on > resume_from,
            )
        )
        session.execute(
            update(HouseRecommendations)
            .where(
                HouseRecommendations.simulation_id == simulation_id,
                HouseRecommendations.resolved_on > resume_from,
            )
            .values(result=None, result_price=None, resolved_on=None)
        )
