from datetime import date

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.candle import CandleDTO
from backend.core.dto.sector import SectorDTO, StockSegmentDTO
from backend.core.dto.series_coverage import OriginCoverageDTO
from backend.core.dto.stock import StockDTO
from backend.core.dto.stock_details import StockDetailsDTO
from backend.core.dto.stock_price_history import StockPriceHistoryDTO
from backend.core.enum import AssetClass, DataOrigin
from backend.core.models.models import (
    Sectors,
    Segments,
    Stock,
    StockPriceHistory,
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
    def add_stock_price_history(
        self, session: Session, stock_price_history: list[StockPriceHistory]
    ) -> None:
        session.add_all(stock_price_history)

    @transactional
    def get_stocks_by_date(
        self, session: Session, current_date: date
    ) -> list[CandleDTO]:
        stocks = session.execute(select(Stock)).scalars().all()
        stocks_with_history: list[CandleDTO] = []
        for stock in stocks:
            ph = (
                session.execute(
                    select(StockPriceHistory)
                    .where(
                        StockPriceHistory.stock_id == stock.id,
                        StockPriceHistory.price_date <= current_date,
                    )
                    .order_by(StockPriceHistory.price_date.desc())
                )
                .scalars()
                .first()
            )
            if ph:
                change = ph.close - ph.open
                change_pct = (change / ph.open * 100) if ph.open != 0 else 0
                stocks_with_history.append(
                    CandleDTO(
                        id=ph.stock.id,
                        ticker=ph.stock.ticker,
                        name=ph.stock.name,
                        asset_class=AssetClass(ph.stock.asset_class),
                        close=ph.close,
                        low=ph.low,
                        high=ph.high,
                        volume=ph.volume,
                        open=ph.open,
                        price_date=ph.price_date,
                        change=round(change, 2),
                        change_pct=f"{change_pct:+.2f}%",
                    )
                )
        return stocks_with_history

    @transactional
    def get_stock_details(
        self, session: Session, ticker: str, current_date: date
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
                )
                .order_by(StockPriceHistory.price_date)
            )
            .scalars()
            .all()
        )

        # Último preço do dia atual
        ph_today = history[-1] if history else None

        return StockDetailsDTO(
            id=stock.id,
            ticker=stock.ticker,
            name=stock.name,
            asset_class=AssetClass(stock.asset_class),
            open=ph_today.open if ph_today else 0,
            close=ph_today.close if ph_today else 0,
            low=ph_today.low if ph_today else 0,
            high=ph_today.high if ph_today else 0,
            volume=ph_today.volume if ph_today else 0,
            price_date=ph_today.price_date if ph_today else current_date,
            change=round(ph_today.close - ph_today.open, 2) if ph_today else 0,
            change_pct=(
                f"{((ph_today.close - ph_today.open) / ph_today.open * 100):+.2f}%"
                if ph_today
                else "0.00%"
            ),
            history=[StockPriceHistoryDTO.from_model(h) for h in history],
        )

    @transactional
    def get_average_volume(
        self, session: Session, ticker: str, until: date, window: int
    ) -> float:
        """Média do volume dos últimos `window` pregões até `until` (inclusive)."""
        recent = (
            select(StockPriceHistory.volume)
            .join(Stock, Stock.id == StockPriceHistory.stock_id)
            .where(Stock.ticker == ticker, StockPriceHistory.price_date <= until)
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
                .where(StockPriceHistory.stock_id == stock_id)
                .order_by(StockPriceHistory.price_date.desc())
            )
            .scalars()
            .first()
        )
        return StockPriceHistoryDTO.from_model(price_history) if price_history else None

    @transactional
    def delete_stock_price_history(self, session: Session, stock_id: int) -> None:
        session.execute(
            delete(StockPriceHistory).where(StockPriceHistory.stock_id == stock_id)
        )

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
        self, session: Session, tickers: list[str], start: date, end: date
    ) -> dict[str, dict[date, float]]:
        """Fechamentos de cada ticker em [start, end], por dia de pregão."""
        rows = session.execute(
            select(Stock.ticker, StockPriceHistory.price_date, StockPriceHistory.close)
            .join(StockPriceHistory, StockPriceHistory.stock_id == Stock.id)
            .where(
                Stock.ticker.in_(tickers),
                StockPriceHistory.price_date.between(start, end),
            )
        ).all()
        closes: dict[str, dict[date, float]] = {ticker: {} for ticker in tickers}
        for ticker, price_date, close in rows:
            closes[ticker][price_date] = close
        return closes

    @transactional
    def get_closes_on(self, session: Session, on: date) -> dict[str, float]:
        """Último fechamento histórico de cada ação até `on` (inclusive)."""
        last = (
            select(
                StockPriceHistory.stock_id,
                func.max(StockPriceHistory.price_date).label("price_date"),
            )
            .where(StockPriceHistory.price_date <= on)
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
        ).all()
        return {ticker: close for ticker, close in rows}
