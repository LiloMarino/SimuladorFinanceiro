from datetime import datetime, timedelta

from flask import current_app

from backend import logger_utils
from backend.database import SessionLocal
from backend.models.models import Ativos, PrecoHistorico

logger = logger_utils.setup_logger(__name__)


class Simulation:
    def __init__(self, start_date: datetime, end_date: datetime):
        self.__speed = 0
        self.__current_date = start_date
        self.__end_date = end_date

    def next_day(self):
        """Avança um dia na simulação."""
        if self.__current_date < self.__end_date:
            self.__current_date += timedelta(days=1)
            logger.info(f"Avançando para o dia {self.get_current_date_formatted()}")
        else:
            logger.info("Fim da simulação")
            raise StopIteration("Fim da simulação")

    def get_current_date_formatted(self) -> str:
        return self.__current_date.strftime("%d/%m/%Y")

    def set_speed(self, speed: int):
        logger.info(f"Velocidade da simulação alterada para {speed}x")
        self.__speed = speed

    def get_speed(self) -> int:
        return self.__speed

    def get_stocks(self) -> list[PrecoHistorico]:
        """Consulta o banco e retorna todos os ativos do dia atual."""
        with SessionLocal() as session:
            # Consulta todos os ativos
            ativos = session.query(Ativos).all()
            stocks = []
            for ativo in ativos:
                ph = (
                    session.query(PrecoHistorico)
                    .filter_by(ativos_id=ativo.ativos_id, time=self.__current_date)
                    .first()
                )
                if ph:
                    stocks.append(
                        {
                            "ticker": ph.ativos.ticker,
                            "name": ph.ativos.nome,
                            "price": ph.close,
                            "low": ph.low,
                            "high": ph.high,
                            "volume": ph.volume,
                            "open": ph.open,  # <-- precisa estar aqui!
                            "date": ph.time.isoformat(),
                        }
                    )
            return stocks

    def get_stock_details(self, ticker: str) -> dict | None:
        with SessionLocal() as session:
            ativo = session.query(Ativos).filter_by(ticker=ticker).first()
            if not ativo:
                return None

            # Histórico até a data atual
            history = (
                session.query(PrecoHistorico)
                .filter(PrecoHistorico.ativos_id == ativo.ativos_id)
                .filter(PrecoHistorico.time <= self.__current_date)
                .order_by(PrecoHistorico.time)
                .all()
            )

            hist_list = [
                {
                    "time": ph.time.isoformat(),
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


def get_simulation() -> Simulation:
    if "simulation" not in current_app.config:
        # Define datas iniciais da simulação
        from_date = datetime(2023, 1, 1)
        to_date = datetime(2026, 8, 18)
        current_app.config["simulation"] = Simulation(from_date, to_date)
    return current_app.config["simulation"]
