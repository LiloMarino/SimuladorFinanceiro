from dataclasses import dataclass
from datetime import date

from backend.core import repository
from backend.core.enum import NewsType
from backend.features.realtime import notify


@dataclass(frozen=True)
class Headline:
    """Uma manchete pronta para o jornal, antes de ganhar data e partida."""

    news_type: NewsType
    text: str
    dek: str | None = None
    tickers: tuple[str, ...] = ()
    # Variação do dia do ativo, em pontos percentuais com sinal
    change_pct: float | None = None
    # As siglas dos partidos que a manchete cita, na ordem do texto, para o selo no jornal
    party_abbrs: tuple[str, ...] = ()


def publish(simulation_id: int, day: date, headline: Headline) -> None:
    """Grava a manchete no histórico da partida e a entrega à sala inteira."""
    news = repository.news.create(
        simulation_id,
        day,
        headline.news_type,
        headline.text,
        headline.dek,
        list(headline.tickers),
        list(headline.party_abbrs),
        headline.change_pct,
    )
    notify("news_published", news.to_json())
