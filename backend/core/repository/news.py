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
        change_pct: float | None = None,
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
                change_pct=change_pct,
                created_at=datetime.now(UTC),
            )
            .returning(News)
        ).one()
        return NewsDTO.model_validate(row)

    @transactional
    def of_month(
        self, session: Session, simulation_id: int, month: date
    ) -> list[NewsDTO]:
        """As manchetes do mês de `month`, da mais nova para a mais antiga; no mesmo dia, a última publicada primeiro."""
        first = month.replace(day=1)
        following = (
            first.replace(year=first.year + 1, month=1)
            if first.month == 12
            else first.replace(month=first.month + 1)
        )
        rows = session.scalars(
            select(News)
            .where(
                News.simulation_id == simulation_id,
                News.news_date >= first,
                News.news_date < following,
            )
            .order_by(News.news_date.desc(), News.id.desc())
        )
        return [NewsDTO.model_validate(row) for row in rows]
