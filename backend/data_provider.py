from datetime import datetime

from backend.database import SessionLocal
from backend.logger_utils import setup_logger
from backend.models.models import Ativos, PrecoHistorico

logger = setup_logger(__name__)


def get_stocks(current_date: datetime) -> list:
    with SessionLocal() as session:
        # Consulta todos os ativos
        ativos = session.query(Ativos).all()
        stocks = []
        for ativo in ativos:
            ph = (
                session.query(PrecoHistorico)
                .filter_by(ativos_id=ativo.ativos_id, time=current_date)
                .first()
            )
            if ph:
                change = ph.close - ph.open
                change_pct = (change / ph.open * 100) if ph.open != 0 else 0
                stocks.append(
                    {
                        "ticker": ph.ativos.ticker,
                        "name": ph.ativos.nome,
                        "price": ph.close,
                        "low": ph.low,
                        "high": ph.high,
                        "volume": ph.volume,
                        "open": ph.open,
                        "date": ph.time.isoformat(),
                        "change": round(change, 2),
                        "change_pct": f"{change_pct:+.2f}%",
                    }
                )
        return stocks


def get_stock_details(ticker: str, current_date: datetime) -> dict | None:
    with SessionLocal() as session:
        ativo = session.query(Ativos).filter_by(ticker=ticker).first()
        if not ativo:
            return None

        # Histórico até a data atual
        history = (
            session.query(PrecoHistorico)
            .filter(PrecoHistorico.ativos_id == ativo.ativos_id)
            .filter(PrecoHistorico.time <= current_date)
            .order_by(PrecoHistorico.time)
            .all()
        )

        hist_list = [
            {
                "date": ph.time.isoformat(),
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
            "ticker": ativo.ticker,
            "name": ativo.nome,
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


def get_all_tickers() -> list[str]:
    """
    Retorna uma lista com todos os tickers cadastrados no banco de dados.

    Returns:
        List[str]: Lista de tickers, ex: ["PETR4", "VALE3", "ITUB4", ...]
    """
    with SessionLocal() as session:
        tickers = [ativo.ticker for ativo in session.query(Ativos.ticker).all()]
        logger.info(f"{len(tickers)} tickers carregados do banco de dados.")
        return tickers


def get_selic_rate() -> float:
    return 0.0


def get_ipca_rate() -> float:
    return 0.0


def get_cdi_rate() -> float:
    return 0.0
