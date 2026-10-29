from datetime import UTC, date, datetime

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.news import NewsDTO
from backend.core.enum import NewsType
from backend.core.models.models import News


class NewsRepository:
    @transactional
    def create(
        self,
        session: Session,
        simulation_id: int,
        news_date: date,
        news_type: NewsType,
        headline: str,
        dek: str | None,
        tickers: list[str],
    ) -> NewsDTO:
        row = session.scalars(
            insert(News)
            .values(
                simulation_id=simulation_id,
                news_date=news_date,
                news_type=news_type.value,
                headline=headline,
                dek=dek,
                tickers=tickers,
                created_at=datetime.now(UTC),
            )
            .returning(News)
        ).one()
        return NewsDTO.model_validate(row)

    @transactional
    def of_simulation(self, session: Session, simulation_id: int) -> list[NewsDTO]:
        """Da mais nova para a mais antiga; no mesmo dia, a última publicada primeiro."""
        rows = session.scalars(
            select(News)
            .where(News.simulation_id == simulation_id)
            .order_by(News.news_date.desc(), News.id.desc())
        )
        return [NewsDTO.model_validate(row) for row in rows]
