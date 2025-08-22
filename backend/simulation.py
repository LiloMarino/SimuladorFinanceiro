from datetime import datetime, timedelta

from flask import current_app

from backend.database import SessionLocal
from backend.models.models import Ativos, PrecoHistorico


class Simulation:
    def __init__(self, start_date: datetime, end_date: datetime):
        self.speed = 0
        self.current_date = start_date
        self.end_date = end_date

    def next_day(self):
        """Avança um dia na simulação."""
        if self.current_date < self.end_date:
            self.current_date += timedelta(days=1)
        else:
            raise StopIteration("Fim da simulação")

    def get_stocks(self) -> list[PrecoHistorico]:
        """Consulta o banco e retorna todos os ativos do dia atual."""
        with SessionLocal() as session:
            # Consulta todos os ativos
            ativos = session.query(Ativos).all()
            stocks = []
            for ativo in ativos:
                ph = (
                    session.query(PrecoHistorico)
                    .filter_by(ativos_id=ativo.ativos_id, time=self.current_date)
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
                            "change": round(ph.close - ph.open, 2),
                            "change_pct": f"{(ph.close - ph.open) / ph.open * 100:+.2f}%",
                        }
                    )
            return stocks


def get_simulation() -> Simulation:
    if "simulation" not in current_app.config:
        # Define datas iniciais da simulação
        from_date = datetime(2025, 8, 11)
        to_date = datetime(2025, 8, 18)
        current_app.config["simulation"] = Simulation(from_date, to_date)
    return current_app.config["simulation"]
