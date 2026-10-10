from bisect import bisect_right
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from itertools import batched

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.fetch_log import FetchLogDTO
from backend.core.dto.series_coverage import OriginCoverageDTO
from backend.core.enum import DataOrigin, IndicatorSeries
from backend.core.models.models import EconomicIndicatorHistory, FetchLog

# Linhas por INSERT: 4 parâmetros por linha ficam abaixo do limite de 65535 do Postgres
UPSERT_CHUNK = 5000


@dataclass(frozen=True)
class IndicatorHistory:
    """Uma série inteira em memória, com os dias em ordem."""

    dates: list[date]
    values: dict[date, Decimal]

    @property
    def start(self) -> date | None:
        return self.dates[0] if self.dates else None

    @property
    def end(self) -> date | None:
        return self.dates[-1] if self.dates else None

    def value_on(self, day: date) -> Decimal | None:
        return self.values.get(day)

    def last_known(self, day: date) -> Decimal | None:
        """Valor do último dia da série até `day`, inclusive."""
        index = bisect_right(self.dates, day)
        return self.values[self.dates[index - 1]] if index else None

    def values_until(self, day: date, count: int) -> list[Decimal]:
        """Os últimos `count` valores da série até `day`, inclusive."""
        index = bisect_right(self.dates, day)
        return [self.values[d] for d in self.dates[max(index - count, 0) : index]]


class EconomicRepository:
    def __init__(self) -> None:
        # O motor lê as séries a cada tick e por posição; o cache só muda quando
        # uma busca grava, e cada troca substitui o dict inteiro
        self._histories: dict[IndicatorSeries, IndicatorHistory] = {}

    def get_history(self, series: IndicatorSeries) -> IndicatorHistory:
        history = self._histories.get(series)
        if history is None:
            history = self._load_history(series)
            self._histories = {**self._histories, series: history}
        return history

    def save_history(
        self, series: IndicatorSeries, rows: list[tuple[date, Decimal]]
    ) -> None:
        self._upsert_history(series, rows)
        self._histories = {k: v for k, v in self._histories.items() if k != series}

    @transactional
    def _load_history(
        self, session: Session, series: IndicatorSeries
    ) -> IndicatorHistory:
        rows = session.execute(
            select(EconomicIndicatorHistory.ref_date, EconomicIndicatorHistory.value)
            .where(EconomicIndicatorHistory.series == series.value)
            .order_by(EconomicIndicatorHistory.ref_date)
        ).all()
        return IndicatorHistory(
            dates=[ref_date for ref_date, _ in rows],
            values={ref_date: value for ref_date, value in rows},
        )

    @transactional
    def _upsert_history(
        self,
        session: Session,
        series: IndicatorSeries,
        rows: list[tuple[date, Decimal]],
    ) -> None:
        for chunk in batched(rows, UPSERT_CHUNK, strict=False):
            statement = insert(EconomicIndicatorHistory).values(
                [
                    {
                        "series": series.value,
                        "ref_date": ref_date,
                        "value": value,
                        "origin": DataOrigin.REAL.value,
                    }
                    for ref_date, value in chunk
                ]
            )
            session.execute(
                statement.on_conflict_do_update(
                    index_elements=["series", "ref_date"],
                    set_={
                        "value": statement.excluded.value,
                        "origin": statement.excluded.origin,
                    },
                )
            )

    @transactional
    def get_last_real_date(
        self, session: Session, series: IndicatorSeries
    ) -> date | None:
        return session.execute(
            select(func.max(EconomicIndicatorHistory.ref_date)).where(
                EconomicIndicatorHistory.series == series.value,
                EconomicIndicatorHistory.origin == DataOrigin.REAL.value,
            )
        ).scalar()

    @transactional
    def get_coverage(self, session: Session) -> list[OriginCoverageDTO]:
        rows = session.execute(
            select(
                EconomicIndicatorHistory.series,
                EconomicIndicatorHistory.origin,
                func.min(EconomicIndicatorHistory.ref_date),
                func.max(EconomicIndicatorHistory.ref_date),
            ).group_by(EconomicIndicatorHistory.series, EconomicIndicatorHistory.origin)
        ).all()
        return [
            OriginCoverageDTO(
                key=series, origin=DataOrigin(origin), start=start, end=end
            )
            for series, origin, start, end in rows
        ]

    @transactional
    def get_fetch_log(
        self, session: Session, series: IndicatorSeries
    ) -> FetchLogDTO | None:
        log = session.get(FetchLog, series.value)
        return FetchLogDTO.model_validate(log) if log else None

    @transactional
    def save_fetch_attempt(
        self,
        session: Session,
        series: IndicatorSeries,
        attempted_at: datetime,
        succeeded: bool,
    ) -> None:
        values = {"series": series.value, "attempted_at": attempted_at}
        if succeeded:
            values["succeeded_at"] = attempted_at
        statement = insert(FetchLog).values(values)
        session.execute(
            statement.on_conflict_do_update(
                index_elements=["series"],
                set_={k: v for k, v in values.items() if k != "series"},
            )
        )
