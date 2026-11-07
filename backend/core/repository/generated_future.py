from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, insert, select
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.generated_future import FutureParamsDTO, GeneratedFutureDTO
from backend.core.dto.series_coverage import SeriesKind
from backend.core.enum import DataOrigin
from backend.core.models.models import (
    EconomicIndicatorHistory,
    GeneratedFuture,
    Stock,
    StockCorporateEvent,
    StockPriceHistory,
)
from backend.core.repository.generated_swap import (
    drop_generated,
    freeze_generated,
    played_periods,
)
from backend.core.repository.series_version import COMMON_VERSION

type PriceRow = tuple[str, date, float, float, float, float, int]
type IndicatorRow = tuple[str, date, Decimal]


@dataclass(frozen=True)
class GeneratedRows:
    """As linhas geradas de uma série, nas colunas da tabela dela, sem chave nem origem."""

    kind: SeriesKind
    key: str
    rows: list[dict]
    # Proventos do ativo (`ex_date`, `kind`, `value`), gravados com as linhas dele
    events: list[dict] = field(default_factory=list)


class GeneratedFutureRepository:
    @transactional
    def get(self, session: Session) -> GeneratedFutureDTO | None:
        future = session.get(GeneratedFuture, 1)
        if future is None:
            return None
        return GeneratedFutureDTO(
            until=future.until,
            seed=future.seed,
            temperature=float(future.temperature),
            inflation_level=float(future.inflation_level),
            surge_frequency=float(future.surge_frequency),
            surge_intensity=float(future.surge_intensity),
            generated_at=future.generated_at,
            real_advanced_until=future.real_advanced_until,
            saved_simulations_on_future=self._count_saved_on_future(session),
        )

    def _count_saved_on_future(self, session: Session) -> int:
        """Partidas salvas que já jogaram algum dia do futuro gerado comum."""
        count = 0
        for _, start, end in played_periods(session):
            count += any(
                session.execute(
                    select(
                        select(model)
                        .where(
                            model.version == COMMON_VERSION,
                            model.origin == DataOrigin.GENERATED.value,
                            day.between(start, end),
                        )
                        .exists()
                    )
                ).scalar_one()
                for model, day in (
                    (StockPriceHistory, StockPriceHistory.price_date),
                    (EconomicIndicatorHistory, EconomicIndicatorHistory.ref_date),
                )
            )
        return count

    @transactional
    def get_real_prices(self, session: Session) -> Sequence[PriceRow]:
        """Todos os pregões reais da série comum, por ativo e em ordem de data."""
        return session.execute(
            select(
                Stock.ticker,
                StockPriceHistory.price_date,
                StockPriceHistory.open,
                StockPriceHistory.high,
                StockPriceHistory.low,
                StockPriceHistory.close,
                StockPriceHistory.volume,
            )
            .join(Stock, Stock.id == StockPriceHistory.stock_id)
            .where(
                StockPriceHistory.version == COMMON_VERSION,
                StockPriceHistory.origin == DataOrigin.REAL.value,
            )
            .order_by(Stock.ticker, StockPriceHistory.price_date)
        ).all()

    @transactional
    def get_real_indicators(self, session: Session) -> Sequence[IndicatorRow]:
        return session.execute(
            select(
                EconomicIndicatorHistory.series,
                EconomicIndicatorHistory.ref_date,
                EconomicIndicatorHistory.value,
            )
            .where(
                EconomicIndicatorHistory.version == COMMON_VERSION,
                EconomicIndicatorHistory.origin == DataOrigin.REAL.value,
            )
            .order_by(
                EconomicIndicatorHistory.series, EconomicIndicatorHistory.ref_date
            )
        ).all()

    @transactional
    def get_real_fingerprint(self, session: Session) -> tuple:
        """Quantas linhas reais e até quando, por série: muda quando o real muda."""
        prices = session.execute(
            select(
                StockPriceHistory.stock_id,
                func.count(),
                func.max(StockPriceHistory.price_date),
            )
            .where(
                StockPriceHistory.version == COMMON_VERSION,
                StockPriceHistory.origin == DataOrigin.REAL.value,
            )
            .group_by(StockPriceHistory.stock_id)
            .order_by(StockPriceHistory.stock_id)
        ).all()
        indicators = session.execute(
            select(
                EconomicIndicatorHistory.series,
                func.count(),
                func.max(EconomicIndicatorHistory.ref_date),
                func.sum(EconomicIndicatorHistory.value),
            )
            .where(
                EconomicIndicatorHistory.version == COMMON_VERSION,
                EconomicIndicatorHistory.origin == DataOrigin.REAL.value,
            )
            .group_by(EconomicIndicatorHistory.series)
            .order_by(EconomicIndicatorHistory.series)
        ).all()
        events = session.execute(
            select(
                StockCorporateEvent.stock_id,
                func.count(),
                func.max(StockCorporateEvent.ex_date),
                func.sum(StockCorporateEvent.value),
            )
            .where(
                StockCorporateEvent.version == COMMON_VERSION,
                StockCorporateEvent.origin == DataOrigin.REAL.value,
            )
            .group_by(StockCorporateEvent.stock_id)
            .order_by(StockCorporateEvent.stock_id)
        ).all()
        return (
            tuple(map(tuple, prices)),
            tuple(map(tuple, indicators)),
            tuple(map(tuple, events)),
        )

    @transactional
    def replace(
        self,
        session: Session,
        params: FutureParamsDTO,
        series: list[GeneratedRows],
        generated_at: datetime,
        on_progress: Callable[[str, int, int], None],
    ) -> None:
        """
        Troca o futuro comum pelo novo numa transação só: as partidas salvas
        guardam o que jogaram, o gerado antigo sai e o novo entra. `on_progress`
        roda antes de cada série e pode interromper a troca levantando exceção,
        o que desfaz tudo.
        """
        for model in (StockPriceHistory, EconomicIndicatorHistory, StockCorporateEvent):
            freeze_generated(session, model, [])
            drop_generated(session, model, [])

        stock_ids = dict(session.execute(select(Stock.ticker, Stock.id)).all())
        for done, generated in enumerate(series, start=1):
            on_progress(generated.key, done, len(series))
            if not generated.rows:
                continue
            if generated.kind is SeriesKind.STOCK:
                model, key = StockPriceHistory, {"stock_id": stock_ids[generated.key]}
            else:
                model, key = EconomicIndicatorHistory, {"series": generated.key}
            session.execute(
                insert(model),
                [
                    {
                        **row,
                        **key,
                        "origin": DataOrigin.GENERATED.value,
                        "version": COMMON_VERSION,
                    }
                    for row in generated.rows
                ],
            )
            if generated.events:
                session.execute(
                    insert(StockCorporateEvent),
                    [
                        {
                            **event,
                            **key,
                            "origin": DataOrigin.GENERATED.value,
                            "version": COMMON_VERSION,
                        }
                        for event in generated.events
                    ],
                )

        values = {
            "seed": params.seed,
            "temperature": Decimal(str(params.temperature)),
            "inflation_level": Decimal(str(params.inflation_level)),
            "surge_frequency": Decimal(str(params.surge_frequency)),
            "surge_intensity": Decimal(str(params.surge_intensity)),
            "until": params.until,
            "generated_at": generated_at,
            "real_advanced_until": None,
        }
        session.execute(
            upsert(GeneratedFuture)
            .values(id=1, **values)
            .on_conflict_do_update(index_elements=["id"], set_=values)
        )
