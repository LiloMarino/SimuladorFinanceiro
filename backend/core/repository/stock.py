from datetime import date

from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.stock import StockDTO
from backend.core.dto.stock_details import StockDetailsDTO
from backend.core.dto.stock_price_history import StockPriceHistoryDTO
from backend.core.models.models import Stock, StockPriceHistory


class StockRepository:
    @transactional
    def add_stock(self, session: Session, ticker: str, name: str) -> Stock:
        stock = Stock(ticker=ticker, name=name)
        session.add(stock)
        return stock

    @transactional
    def add_stock_price_history(
        self, session: Session, stock_price_history: list[StockPriceHistory]
    ):
        session.add_all(stock_price_history)

    @transactional
    def get_stocks_by_date(
        self, session: Session, current_date: date
    ) -> list[StockDTO]:
        stocks = session.query(Stock).all()
        stocks_with_history: list[StockDTO] = []
        for stock in stocks:
            ph = (
                session.query(StockPriceHistory)
                .filter_by(stock_id=stock.id, price_date=current_date)
                .first()
            )
            if ph:
                change = ph.close - ph.open
                change_pct = (change / ph.open * 100) if ph.open != 0 else 0
                stocks_with_history.append(
                    StockDTO(
                        ticker=ph.stock.ticker,
                        name=ph.stock.name,
                        price=ph.close,
                        low=ph.low,
                        high=ph.high,
                        volume=ph.volume,
                        open=ph.open,
                        date=ph.price_date.isoformat(),
                        change=round(change, 2),
                        change_pct=f"{change_pct:+.2f}%",
                    )
                )
        return stocks_with_history

    @transactional
    def get_stock_details(
        self, session: Session, ticker: str, current_date: date
    ) -> StockDetailsDTO | None:
        stock = session.query(Stock).filter_by(ticker=ticker).first()
        if not stock:
            return None

        # Histórico até a data atual
        history: list[StockPriceHistory] = (
            session.query(StockPriceHistory)
            .filter(StockPriceHistory.stock_id == stock.id)
            .filter(StockPriceHistory.price_date <= current_date)
            .order_by(StockPriceHistory.price_date)
            .all()
        )

        # Último preço do dia atual
        ph_today = history[-1] if history else None

        return StockDetailsDTO(
            ticker=stock.ticker,
            name=stock.name,
            price=ph_today.close if ph_today else 0,
            low=ph_today.low if ph_today else 0,
            high=ph_today.high if ph_today else 0,
            volume=ph_today.volume if ph_today else 0,
            change=round(ph_today.close - ph_today.open, 2) if ph_today else 0,
            change_pct=(
                f"{((ph_today.close - ph_today.open) / ph_today.open * 100):+.2f}%"
                if ph_today
                else "0.00%"
            ),
            history=[StockPriceHistoryDTO.from_model(h) for h in history],
        )

    @transactional
    def get_by_ticker(self, session: Session, ticker: str) -> Stock | None:
        return session.query(Stock).filter_by(ticker=ticker).first()

    @transactional
    def get_last_stock_price_history(
        self, session: Session, stock_id: int
    ) -> StockPriceHistory | None:
        return (
            session.query(StockPriceHistory)
            .filter_by(stock_id=stock_id)
            .order_by(StockPriceHistory.price_date.desc())
            .first()
        )

    @transactional
    def delete_stock_price_history(self, session: Session, stock_id: int):
        session.query(StockPriceHistory).filter_by(stock_id=stock_id).delete()
