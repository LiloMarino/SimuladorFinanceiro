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

    def get_stock_details(self, session: Session, ticker: str, current_date: date):
        stock = session.query(Stock).filter_by(ticker=ticker).first()
        if not stock:
            return None

        # Histórico até a data atual
        history = (
            session.query(StockPriceHistory)
            .filter(StockPriceHistory.stock_id == stock.id)
            .filter(StockPriceHistory.price_date <= current_date)
            .order_by(StockPriceHistory.price_date)
            .all()
        )

        hist_list = [
            {
                "date": ph.price_date.isoformat(),
                "close": ph.close,
                "open": ph.open,
                "low": ph.low,
                "high": ph.high,
                "volume": ph.volume,
            }
            for ph in history
        ]

        # Último preço do dia atual
        ph_today = hist_list[-1] if hist_list else None

        return {
            "ticker": stock.ticker,
            "name": stock.name,
            "price": ph_today["close"] if ph_today else 0,
            "low": ph_today["low"] if ph_today else 0,
            "high": ph_today["high"] if ph_today else 0,
            "volume": ph_today["volume"] if ph_today else 0,
            "change": (
                round(ph_today["close"] - ph_today["open"], 2) if ph_today else 0
            ),
            "change_pct": (
                f"{((ph_today['close'] - ph_today['open']) / ph_today['open'] * 100):+.2f}%"
                if ph_today
                else "0.00%"
            ),
            "history": hist_list,
        }
