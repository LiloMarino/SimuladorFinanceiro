from datetime import date

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.candle_challenge import ChallengeRecordDTO
from backend.core.models.models import CandleChallenges, Users


class CandleChallengeRepository:
    @transactional
    def create(
        self,
        session: Session,
        record: ChallengeRecordDTO,
    ) -> bool:
        """Grava a resposta; falso quando o jogador já respondeu esse padrão."""
        created = session.scalar(
            insert(CandleChallenges)
            .values(
                simulation_id=record.simulation_id,
                user_id=record.user_id,
                ticker=record.ticker,
                pattern_date=record.pattern_date,
                pattern_code=record.pattern_code,
                direction=record.direction,
                answered_on=record.answered_on,
            )
            .on_conflict_do_nothing()
            .returning(CandleChallenges.pattern_date)
        )
        return created is not None

    @transactional
    def get(
        self,
        session: Session,
        simulation_id: int,
        user_id: int,
        ticker: str,
        pattern_date: date,
    ) -> ChallengeRecordDTO | None:
        row = session.get(
            CandleChallenges, (simulation_id, user_id, ticker, pattern_date)
        )
        return ChallengeRecordDTO.model_validate(row) if row else None

    @transactional
    def latest(
        self, session: Session, simulation_id: int, user_id: int, ticker: str
    ) -> ChallengeRecordDTO | None:
        """A resposta mais recente do jogador nesse ativo."""
        row = session.scalars(
            select(CandleChallenges)
            .where(
                CandleChallenges.simulation_id == simulation_id,
                CandleChallenges.user_id == user_id,
                CandleChallenges.ticker == ticker,
            )
            .order_by(CandleChallenges.pattern_date.desc())
            .limit(1)
        ).first()
        return ChallengeRecordDTO.model_validate(row) if row else None

    @transactional
    def waiting(self, session: Session, simulation_id: int) -> list[ChallengeRecordDTO]:
        """As respostas de todos os jogadores que ainda esperam o 5º pregão."""
        rows = session.scalars(
            select(CandleChallenges).where(
                CandleChallenges.simulation_id == simulation_id,
                CandleChallenges.result.is_(None),
            )
        )
        return [ChallengeRecordDTO.model_validate(row) for row in rows]

    @transactional
    def settle(
        self,
        session: Session,
        record: ChallengeRecordDTO,
        result: str,
        settled_on: date,
    ) -> None:
        session.execute(
            update(CandleChallenges)
            .where(
                CandleChallenges.simulation_id == record.simulation_id,
                CandleChallenges.user_id == record.user_id,
                CandleChallenges.ticker == record.ticker,
                CandleChallenges.pattern_date == record.pattern_date,
            )
            .values(result=result, settled_on=settled_on)
        )

    @transactional
    def score(
        self, session: Session, simulation_id: int, user_id: int
    ) -> tuple[int, int]:
        """`(acertos, respondidas)` entre as conferidas; as anuladas não contam."""
        hits, answered = session.execute(
            select(
                func.count().filter(CandleChallenges.result == "hit"),
                func.count().filter(CandleChallenges.result.in_(["hit", "miss"])),
            ).where(
                CandleChallenges.simulation_id == simulation_id,
                CandleChallenges.user_id == user_id,
            )
        ).one()
        return hits, answered

    @transactional
    def ranking(
        self, session: Session, simulation_ids: list[int]
    ) -> list[tuple[str, int, int]]:
        """`(apelido, acertos, respondidas)` de quem tem alguma resposta conferida."""
        rows = session.execute(
            select(
                Users.nickname,
                func.count().filter(CandleChallenges.result == "hit"),
                func.count(),
            )
            .join(Users, Users.id == CandleChallenges.user_id)
            .where(
                CandleChallenges.simulation_id.in_(simulation_ids),
                CandleChallenges.result.in_(["hit", "miss"]),
            )
            .group_by(Users.nickname)
        ).all()
        return [(nickname, hits, answered) for nickname, hits, answered in rows]

    @transactional
    def rewind(self, session: Session, simulation_id: int, resume_from: date) -> None:
        """
        Prepara a retomada: as respostas dadas depois do último dia processado saem, e
        as conferências depois dele voltam a esperar.
        """
        session.execute(
            delete(CandleChallenges).where(
                CandleChallenges.simulation_id == simulation_id,
                CandleChallenges.answered_on > resume_from,
            )
        )
        session.execute(
            update(CandleChallenges)
            .where(
                CandleChallenges.simulation_id == simulation_id,
                CandleChallenges.settled_on > resume_from,
            )
            .values(result=None, settled_on=None)
        )
