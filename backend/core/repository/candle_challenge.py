from datetime import date

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.models.models import CandleChallengeStats


class CandleChallengeRepository:
    @transactional
    def add_hits(self, session: Session, user_id: int, hits: int) -> int:
        """Soma acertos ao total do jogador e devolve o total novo."""
        return (
            session.scalar(
                insert(CandleChallengeStats)
                .values(user_id=user_id, hits=hits)
                .on_conflict_do_update(
                    index_elements=["user_id"],
                    set_={"hits": CandleChallengeStats.hits + hits},
                )
                .returning(CandleChallengeStats.hits)
            )
            or 0
        )

    @transactional
    def total_hits(self, session: Session, user_id: int) -> int:
        """Os acertos do jogador no desafio, em todas as rodadas."""
        return (
            session.scalar(
                select(CandleChallengeStats.hits).where(
                    CandleChallengeStats.user_id == user_id
                )
            )
            or 0
        )

    @transactional
    def record(self, session: Session, user_id: int) -> tuple[int, date | None]:
        """`(maior sequência, dia em que saiu)`; `(0, None)` para quem nunca jogou."""
        row = session.execute(
            select(
                CandleChallengeStats.best_streak, CandleChallengeStats.best_streak_on
            ).where(CandleChallengeStats.user_id == user_id)
        ).first()
        return (row[0], row[1]) if row else (0, None)

    @transactional
    def save_record(
        self, session: Session, user_id: int, streak: int, reached_on: date
    ) -> None:
        """Grava a sequência como recorde quando ela passa a anterior."""
        stmt = insert(CandleChallengeStats).values(
            user_id=user_id, best_streak=streak, best_streak_on=reached_on
        )
        session.execute(
            stmt.on_conflict_do_update(
                index_elements=["user_id"],
                set_={"best_streak": streak, "best_streak_on": reached_on},
                where=CandleChallengeStats.best_streak < streak,
            )
        )
