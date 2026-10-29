"""
Os marcos históricos: manchetes curadas à mão com data, texto e ativos ligados. Só saem
em período real; o futuro gerado começa depois do último dia real, então nenhum marco
datado cai nele.
"""

from dataclasses import dataclass
from datetime import date

from backend.core.enum import NewsType
from backend.features.newsroom.market import MarketDay
from backend.features.notifications.news import Headline


@dataclass(frozen=True)
class Milestone:
    day: date
    headline: str
    dek: str
    tickers: tuple[str, ...] = ()


MILESTONES: tuple[Milestone, ...] = (
    Milestone(
        date(2008, 9, 15),
        "Lehman Brothers pede falência e a crise global chega às bolsas",
        "O banco americano quebra, e os mercados do mundo inteiro entram em queda.",
    ),
    Milestone(
        date(2011, 8, 8),
        "Bolsas despencam depois do rebaixamento da nota dos EUA",
        "A agência S&P tirou a nota máxima da dívida americana na sexta-feira.",
    ),
    Milestone(
        date(2013, 5, 22),
        "Fed sinaliza o fim dos estímulos e os emergentes sofrem",
        "O presidente do banco central americano fala em reduzir a compra de títulos.",
    ),
    Milestone(
        date(2015, 9, 9),
        "S&P tira o grau de investimento do Brasil",
        "A agência rebaixa a nota do país para BB+, abaixo do selo de bom pagador.",
    ),
    Milestone(
        date(2016, 6, 24),
        "Brexit: britânicos votam pela saída da União Europeia",
        "As bolsas caem no mundo todo com a surpresa do resultado.",
    ),
    Milestone(
        date(2016, 11, 9),
        "Trump vence a eleição americana",
        "A vitória inesperada mexe com os mercados no mundo todo.",
    ),
    Milestone(
        date(2017, 5, 18),
        "Joesley Day: Ibovespa cai 8,8% e o pregão para",
        "A delação da JBS atinge o presidente Temer, e a bolsa para por 30 minutos.",
        ("JBSS3",),
    ),
    Milestone(
        date(2018, 5, 21),
        "Greve dos caminhoneiros paralisa estradas e abastecimento",
        "Os protestos contra o preço do diesel pressionam as ações da Petrobras.",
        ("PETR4",),
    ),
    Milestone(
        date(2019, 7, 10),
        "Câmara aprova a reforma da Previdência em primeiro turno",
        "A bolsa acompanha o avanço da principal pauta econômica do governo.",
    ),
    Milestone(
        date(2020, 3, 9),
        "Covid-19 derruba a bolsa e o pregão para",
        "O circuit breaker é acionado com o avanço do coronavírus e a queda do petróleo.",
    ),
    Milestone(
        date(2020, 3, 11),
        "OMS declara a pandemia de Covid-19",
        "Os países passam a fechar fronteiras, e os mercados seguem em queda.",
    ),
    Milestone(
        date(2020, 4, 20),
        "Petróleo americano fecha negativo pela primeira vez",
        "Sem onde armazenar, quem tinha contratos pagava para se livrar do barril.",
        ("PETR4",),
    ),
    Milestone(
        date(2022, 2, 24),
        "Rússia invade a Ucrânia e as bolsas despencam",
        "O petróleo e o trigo disparam com o início da guerra.",
    ),
    Milestone(
        date(2023, 3, 10),
        "Silicon Valley Bank quebra e reacende o temor com os bancos",
        "O banco americano é fechado pelos reguladores em poucos dias de corrida aos saques.",
    ),
)


def historical_milestones(market: MarketDay) -> list[Headline]:
    """Os marcos que caíram desde o pregão anterior; o que cai no fim de semana sai na segunda."""
    if market.real_until is None:
        return []
    return [
        Headline(NewsType.HISTORICAL_MILESTONE, m.headline, m.dek, m.tickers)
        for m in MILESTONES
        if market.previous < m.day <= min(market.day, market.real_until)
    ]
