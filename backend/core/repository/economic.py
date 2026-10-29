from bisect import bisect_right
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from itertools import batched
from typing import Protocol

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.fetch_log import FetchLogDTO
from backend.core.dto.generated_future import ReplacedGeneratedDTO
from backend.core.dto.series_coverage import OriginCoverageDTO
from backend.core.enum import DataOrigin, IndicatorSeries
from backend.core.models.models import EconomicIndicatorHistory, FetchLog
from backend.core.repository.generated_swap import swap_generated_for_real
from backend.core.repository.series_version import (
    COMMON_VERSION,
    reading_version,
    seen_by,
)

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


class EconomyAdjustment(Protocol):
    """O efeito que uma partida soma por cima das séries guardadas e do preço das ações."""

    def adjust(
        self, series: IndicatorSeries, history: IndicatorHistory
    ) -> IndicatorHistory: ...

    def stock_factor(self, ticker: str, day: date) -> float: ...


class EconomicRepository:
    def __init__(self) -> None:
        # O motor lê as séries a cada tick e por posição; o cache, por série e
        # versão, só muda quando algo grava, e cada troca substitui o dict inteiro
        self._histories: dict[tuple[IndicatorSeries, int], IndicatorHistory] = {}
        # A série como a partida a lê, com o efeito do governo por cima da guardada
        self._adjusted: dict[tuple[IndicatorSeries, int], IndicatorHistory] = {}
        self._adjustments: dict[int, EconomyAdjustment] = {}

    def get_history(
        self,
        series: IndicatorSeries,
        simulation_id: int | None = None,
        *,
        stored: bool = False,
    ) -> IndicatorHistory:
        """A série da partida; com `stored`, a guardada, sem o efeito das medidas do governo."""
        key = (series, reading_version(simulation_id))
        history = self._histories.get(key)
        if history is None:
            history = self._load_history(*key)
            self._histories = {**self._histories, key: history}
        adjustment = self._adjustments.get(key[1])
        if stored or adjustment is None:
            return history
        adjusted = self._adjusted.get(key)
        if adjusted is None:
            adjusted = adjustment.adjust(series, history)
            self._adjusted = {**self._adjusted, key: adjusted}
        return adjusted

    def use_adjustment(self, simulation_id: int, adjustment: EconomyAdjustment) -> None:
        """A partida passa a ler as séries e os preços com o efeito de `adjustment`."""
        self._adjustments = {**self._adjustments, simulation_id: adjustment}
        self.refresh_adjusted(simulation_id)

    def refresh_adjusted(self, simulation_id: int) -> None:
        """Descarta as séries com efeito da partida: a próxima leitura as refaz."""
        self._adjusted = {
            key: history
            for key, history in self._adjusted.items()
            if key[1] != simulation_id
        }

    def stock_factor(self, simulation_id: int, ticker: str, day: date) -> float:
        """O quanto o efeito do governo move o preço da ação no dia; 1 sem efeito."""
        adjustment = self._adjustments.get(simulation_id)
        return 1.0 if adjustment is None else adjustment.stock_factor(ticker, day)

    def save_history(
        self, series: IndicatorSeries, rows: list[tuple[date, Decimal]]
    ) -> ReplacedGeneratedDTO | None:
        """Grava valores reais e devolve os dias gerados que eles ocuparam."""
        replaced = self._upsert_history(series, rows)
        self.clear_cache()
        return replaced

    def clear_cache(self) -> None:
        self._histories = {}
        self._adjusted = {}

    @transactional
    def _load_history(
        self, session: Session, series: IndicatorSeries, version: int
    ) -> IndicatorHistory:
        rows = session.execute(
            select(EconomicIndicatorHistory.ref_date, EconomicIndicatorHistory.value)
            .where(
                EconomicIndicatorHistory.series == series.value,
                seen_by(EconomicIndicatorHistory, version),
            )
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
    ) -> ReplacedGeneratedDTO | None:
        if not rows:
            return None
        # O gerado que o real cobre sai antes do upsert, já copiado para as
        # partidas salvas que o jogaram
        replaced = swap_generated_for_real(
            session,
            EconomicIndicatorHistory,
            [EconomicIndicatorHistory.series == series.value],
            max(ref_date for ref_date, _ in rows),
        )
        for chunk in batched(rows, UPSERT_CHUNK, strict=False):
            statement = insert(EconomicIndicatorHistory).values(
                [
                    {
                        "series": series.value,
                        "ref_date": ref_date,
                        "value": value,
                        "origin": DataOrigin.REAL.value,
                        "version": COMMON_VERSION,
                    }
                    for ref_date, value in chunk
                ]
            )
            session.execute(
                statement.on_conflict_do_update(
                    index_elements=["series", "ref_date", "version"],
                    set_={
                        "value": statement.excluded.value,
                        "origin": statement.excluded.origin,
                    },
                )
            )
        return replaced

    @transactional
    def get_last_real_date(
        self, session: Session, series: IndicatorSeries
    ) -> date | None:
        return session.execute(
            select(func.max(EconomicIndicatorHistory.ref_date)).where(
                EconomicIndicatorHistory.series == series.value,
                EconomicIndicatorHistory.origin == DataOrigin.REAL.value,
                EconomicIndicatorHistory.version == COMMON_VERSION,
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
            )
            .where(EconomicIndicatorHistory.version == COMMON_VERSION)
            .group_by(EconomicIndicatorHistory.series, EconomicIndicatorHistory.origin)
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
