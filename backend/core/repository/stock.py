from datetime import date

from sqlalchemy import delete, func, select, true
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, aliased, selectinload

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.candle import CandleDTO
from backend.core.dto.generated_future import ReplacedGeneratedDTO
from backend.core.dto.sector import SectorDTO, StockSegmentDTO
from backend.core.dto.series_coverage import OriginCoverageDTO
from backend.core.dto.stock import StockDTO
from backend.core.dto.stock_details import StockDetailsDTO
from backend.core.dto.stock_price_history import StockPriceHistoryDTO
from backend.core.dto.ticker_profile import TickerProfileDTO
from backend.core.enum import AssetClass, DataOrigin
from backend.core.models.models import (
    Sectors,
    Segments,
    Stock,
    StockPriceHistory,
    TickerProfile,
)
from backend.core.repository.generated_swap import (
    drop_generated,
    freeze_generated,
    mark_real_advanced,
    swap_generated_for_real,
)
from backend.core.repository.series_version import (
    COMMON_VERSION,
    reading_version,
    seen_by,
)


class StockRepository:
    @transactional
    def add_stock(
        self, session: Session, ticker: str, name: str, asset_class: AssetClass
    ) -> StockDTO:
        stock = Stock(ticker=ticker, name=name, asset_class=asset_class.value)
        session.add(stock)
        session.flush()
        return StockDTO.from_model(stock)

    @transactional
    def save_real_prices(
        self,
        session: Session,
        stock_id: int,
        rows: list[StockPriceHistory],
        overwrite: bool = False,
    ) -> ReplacedGeneratedDTO | None:
        """
        Grava pregões reais. `overwrite` troca o histórico comum inteiro, gerado
        junto; sem ele, o real ocupa o lugar do gerado nos dias que cobre.
        """
        if not rows:
            return None
        same_stock = [StockPriceHistory.stock_id == stock_id]
        real_end = max(row.price_date for row in rows)
        replaced = None
        if overwrite:
            freeze_generated(session, StockPriceHistory, same_stock)
            if drop_generated(session, StockPriceHistory, same_stock) is not None:
                mark_real_advanced(session, real_end)
            session.execute(
                delete(StockPriceHistory).where(
                    *same_stock, StockPriceHistory.version == COMMON_VERSION
                )
            )
        else:
            replaced = swap_generated_for_real(
                session, StockPriceHistory, same_stock, real_end
            )
        session.add_all(rows)
        return replaced

    @transactional
    def get_stocks_by_date(
        self, session: Session, current_date: date, simulation_id: int | None = None
    ) -> list[CandleDTO]:
        """Última cotação de cada ativo, em uma consulta com busca limitada pelo índice."""
        seen = seen_by(StockPriceHistory, reading_version(simulation_id))
        latest = (
            select(StockPriceHistory)
            .where(
                StockPriceHistory.stock_id == Stock.id,
                StockPriceHistory.price_date <= current_date,
                seen,
            )
            .order_by(StockPriceHistory.price_date.desc())
            .limit(1)
            .lateral()
        )
        price = aliased(StockPriceHistory, latest)
        rows = session.execute(
            select(Stock, price)
            .select_from(Stock)
            .join(latest, true())
            .order_by(Stock.id)
        ).all()
        return [CandleDTO.from_prices(stock, history) for stock, history in rows]

    @transactional
    def get_recent_closes(
        self,
        session: Session,
        current_date: date,
        days: int,
        simulation_id: int | None = None,
    ) -> dict[str, list[float]]:
        """Os últimos `days` fechamentos de cada ação até `current_date`, em ordem cronológica."""
        seen = seen_by(StockPriceHistory, reading_version(simulation_id))
        # O prefixo (stock_id, price_date) do índice busca a janela por ativo,
        # sem percorrer todo o histórico para numerar as linhas de cada série.
        recent = (
            select(StockPriceHistory.price_date, StockPriceHistory.close)
            .where(
                StockPriceHistory.stock_id == Stock.id,
                StockPriceHistory.price_date <= current_date,
                seen,
            )
            .order_by(StockPriceHistory.price_date.desc())
            .limit(days)
            .lateral()
        )
        rows = session.execute(
            select(Stock.ticker, recent.c.close)
            .select_from(Stock)
            .outerjoin(recent, true())
            .order_by(Stock.id, recent.c.price_date)
        ).all()
        closes: dict[str, list[float]] = {}
        for ticker, close in rows:
            values = closes.setdefault(ticker, [])
            if close is not None:
                values.append(close)
        return closes

    @transactional
    def get_stock_details(
        self,
        session: Session,
        ticker: str,
        current_date: date,
        simulation_id: int | None = None,
    ) -> StockDetailsDTO | None:
        stock = session.execute(
            select(Stock).where(Stock.ticker == ticker)
        ).scalar_one_or_none()
        if not stock:
            return None

        # Histórico até a data atual
        history: list[StockPriceHistory] = list(
            session.execute(
                select(StockPriceHistory)
                .where(
                    StockPriceHistory.stock_id == stock.id,
                    StockPriceHistory.price_date <= current_date,
                    seen_by(StockPriceHistory, reading_version(simulation_id)),
                )
                .order_by(StockPriceHistory.price_date)
            )
            .scalars()
            .all()
        )

        # Último preço do dia atual
        ph_today = (
            history[-1]
            if history
            else StockPriceHistoryDTO(
                open=0, close=0, high=0, low=0, volume=0, price_date=current_date
            )
        )
        candle = CandleDTO.from_prices(stock, ph_today)

        return StockDetailsDTO(
            **candle.model_dump(),
            history=[StockPriceHistoryDTO.from_model(h) for h in history],
        )

    @transactional
    def get_average_volume(
        self,
        session: Session,
        ticker: str,
        until: date,
        window: int,
        simulation_id: int | None = None,
    ) -> float:
        """Média do volume dos últimos `window` pregões até `until` (inclusive)."""
        recent = (
            select(StockPriceHistory.volume)
            .join(Stock, Stock.id == StockPriceHistory.stock_id)
            .where(
                Stock.ticker == ticker,
                StockPriceHistory.price_date <= until,
                seen_by(StockPriceHistory, reading_version(simulation_id)),
            )
            .order_by(StockPriceHistory.price_date.desc())
            .limit(window)
            .subquery()
        )
        average = session.execute(select(func.avg(recent.c.volume))).scalar_one()
        return float(average) if average is not None else 0.0

    @transactional
    def get_by_ticker(self, session: Session, ticker: str) -> StockDTO | None:
        stock = session.execute(
            select(Stock).where(Stock.ticker == ticker)
        ).scalar_one_or_none()
        return StockDTO.from_model(stock) if stock else None

    @transactional
    def set_asset_class(
        self, session: Session, ticker: str, asset_class: AssetClass
    ) -> StockDTO | None:
        stock = session.execute(
            select(Stock).where(Stock.ticker == ticker)
        ).scalar_one_or_none()
        if not stock:
            return None
        stock.asset_class = asset_class.value
        return StockDTO.from_model(stock)

    @transactional
    def get_last_stock_price_history(
        self, session: Session, stock_id: int
    ) -> StockPriceHistoryDTO | None:
        price_history = (
            session.execute(
                select(StockPriceHistory)
                .where(
                    StockPriceHistory.stock_id == stock_id,
                    StockPriceHistory.version == COMMON_VERSION,
                    StockPriceHistory.origin == DataOrigin.REAL.value,
                )
                .order_by(StockPriceHistory.price_date.desc())
                .limit(1)
            )
            .scalars()
            .first()
        )
        return StockPriceHistoryDTO.from_model(price_history) if price_history else None

    @transactional
    def get_coverage(self, session: Session) -> list[OriginCoverageDTO]:
        rows = session.execute(
            select(
                Stock.ticker,
                StockPriceHistory.origin,
                func.min(StockPriceHistory.price_date),
                func.max(StockPriceHistory.price_date),
            )
            .join(StockPriceHistory, StockPriceHistory.stock_id == Stock.id)
            .where(StockPriceHistory.version == COMMON_VERSION)
            .group_by(Stock.ticker, StockPriceHistory.origin)
        ).all()
        return [
            OriginCoverageDTO(
                key=ticker, origin=DataOrigin(origin), start=start, end=end
            )
            for ticker, origin, start, end in rows
        ]

    @transactional
    def get_stocks(self, session: Session) -> list[StockDTO]:
        """Todas as ações, inclusive as que ainda não têm preço, em ordem de ticker."""
        stocks = session.execute(select(Stock).order_by(Stock.ticker)).scalars().all()
        return [StockDTO.from_model(stock) for stock in stocks]

    @transactional
    def get_ticker_profile(
        self, session: Session, ticker: str
    ) -> TickerProfileDTO | None:
        """O perfil guardado do código, ou None quando o yfinance ainda não foi consultado."""
        profile = session.get(TickerProfile, ticker)
        return TickerProfileDTO.from_model(profile) if profile else None

    @transactional
    def save_ticker_profile(self, session: Session, profile: TickerProfileDTO) -> None:
        """Grava (ou troca) o perfil do código; o perfil vazio também vale, para o ativo
        que o yfinance devolve sem dado não ser consultado de novo."""
        values = profile.model_dump()
        session.execute(
            insert(TickerProfile)
            .values(**values)
            .on_conflict_do_update(
                index_elements=[TickerProfile.ticker],
                set_={**values, "fetched_at": func.now()},
            )
        )

    @transactional
    def classify(
        self, session: Session, ticker: str, segment: StockSegmentDTO | None
    ) -> StockDTO | None:
        """
        Põe a ação no setor e segmento informados, criando-os pelo nome quando
        ainda não existem; None tira a classificação. Setor e segmento sem
        nenhuma ação saem junto, então a lista de sugestões só tem o que está em uso.
        """
        stock = session.execute(
            select(Stock).where(Stock.ticker == ticker)
        ).scalar_one_or_none()
        if not stock:
            return None

        stock.segment_id = (
            self._get_or_create_segment(session, segment).id if segment else None
        )
        session.flush()
        session.execute(
            delete(Segments).where(
                ~select(Stock.id).where(Stock.segment_id == Segments.id).exists()
            )
        )
        session.execute(
            delete(Sectors).where(
                ~select(Segments.id).where(Segments.sector_id == Sectors.id).exists()
            )
        )
        return StockDTO.from_model(stock)

    def _get_or_create_segment(
        self, session: Session, segment: StockSegmentDTO
    ) -> Segments:
        sector = session.execute(
            select(Sectors).where(Sectors.name == segment.sector)
        ).scalar_one_or_none()
        if not sector:
            sector = Sectors(name=segment.sector)
            session.add(sector)
            session.flush()

        row = session.execute(
            select(Segments).where(
                Segments.sector_id == sector.id, Segments.name == segment.segment
            )
        ).scalar_one_or_none()
        if not row:
            row = Segments(sector_id=sector.id, name=segment.segment)
            session.add(row)
            session.flush()
        return row

    @transactional
    def get_classification(self, session: Session) -> dict[str, StockSegmentDTO]:
        """Setor e segmento de cada ação classificada, pelo ticker."""
        rows = session.execute(
            select(Stock.ticker, Sectors.name, Segments.name)
            .join(Segments, Segments.id == Stock.segment_id)
            .join(Sectors, Sectors.id == Segments.sector_id)
        ).all()
        return {
            ticker: StockSegmentDTO(sector=sector, segment=segment)
            for ticker, sector, segment in rows
        }

    @transactional
    def get_sectors(self, session: Session) -> list[SectorDTO]:
        sectors = (
            session.execute(
                select(Sectors)
                .options(selectinload(Sectors.segments))
                .order_by(Sectors.name)
            )
            .scalars()
            .all()
        )
        return [
            SectorDTO(
                name=sector.name,
                segments=sorted(segment.name for segment in sector.segments),
            )
            for sector in sectors
        ]

    @transactional
    def get_closes_between(
        self,
        session: Session,
        tickers: list[str],
        start: date,
        end: date,
        simulation_id: int | None = None,
    ) -> dict[str, dict[date, float]]:
        """Fechamentos de cada ticker em [start, end], por dia de pregão."""
        rows = session.execute(
            select(Stock.ticker, StockPriceHistory.price_date, StockPriceHistory.close)
            .join(StockPriceHistory, StockPriceHistory.stock_id == Stock.id)
            .where(
                Stock.ticker.in_(tickers),
                StockPriceHistory.price_date.between(start, end),
                seen_by(StockPriceHistory, reading_version(simulation_id)),
            )
        ).all()
        closes: dict[str, dict[date, float]] = {ticker: {} for ticker in tickers}
        for ticker, price_date, close in rows:
            closes[ticker][price_date] = close
        return closes

    @transactional
    def get_closes_on(
        self, session: Session, on: date, simulation_id: int | None = None
    ) -> dict[str, float]:
        """Último fechamento histórico de cada ação até `on` (inclusive)."""
        seen = seen_by(StockPriceHistory, reading_version(simulation_id))
        last = (
            select(
                StockPriceHistory.stock_id,
                func.max(StockPriceHistory.price_date).label("price_date"),
            )
            .where(StockPriceHistory.price_date <= on, seen)
            .group_by(StockPriceHistory.stock_id)
            .subquery()
        )
        rows = session.execute(
            select(Stock.ticker, StockPriceHistory.close)
            .join(StockPriceHistory, StockPriceHistory.stock_id == Stock.id)
            .join(
                last,
                (last.c.stock_id == StockPriceHistory.stock_id)
                & (last.c.price_date == StockPriceHistory.price_date),
            )
            .where(seen)
        ).all()
        return {ticker: close for ticker, close in rows}
