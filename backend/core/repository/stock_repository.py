from datetime import date

from sqlalchemy.orm import Session

from backend.core.decorators.transactional_class import transactional_class
from backend.core.models.models import Stock, StockPriceHistory


@transactional_class
class StockRepository:
    def get_stocks_by_date(self, session: Session, current_date: date):
        stocks = session.query(Stock).all()
        stocks_with_history = []
        for stock in stocks:
            ph = (
                session.query(StockPriceHistory)
                .filter_by(stock_id=stock.id, time=current_date)
                .first()
            )
            if ph:
                change = ph.close - ph.open
                change_pct = (change / ph.open * 100) if ph.open != 0 else 0
                stocks_with_history.append(
                    {
                        "ticker": ph.stock.ticker,
                        "name": ph.stock.name,
                        "price": ph.close,
                        "low": ph.low,
                        "high": ph.high,
                        "volume": ph.volume,
                        "open": ph.open,
                        "date": ph.price_date.isoformat(),
                        "change": round(change, 2),
                        "change_pct": f"{change_pct:+.2f}%",
                    }
                )
        return stocks_with_history
