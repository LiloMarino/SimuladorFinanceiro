"""As manchetes das empresas: movimento forte no dia e máxima de 52 semanas."""

from collections.abc import Sequence

from backend.core.enum import AssetClass, NewsType
from backend.features.newsroom.causes import cause_for
from backend.features.newsroom.market import MarketDay, Quote
from backend.features.newsroom.text import number, pick, price, short_name
from backend.features.notifications.news import Headline

# Variação do dia, em fração, acima da qual o movimento vira manchete
MOVE_THRESHOLD = 0.05
# Acima deste tamanho o verbo sobe de tom: "salta" no lugar de "avança"
BIG_MOVE = 0.08
# Quantos ativos uma regra põe no jornal por pregão: o resto da rajada fica de fora
MAX_PER_DAY = 3
# A janela de um ano de pregões e o mínimo de histórico para chamar de máxima de 52 semanas
YEAR_SESSIONS = 252
MIN_SESSIONS = 126
# A cripto se move assim todo dia, e a variação dela não é notícia de empresa
MOVER_CLASSES = (AssetClass.STOCK, AssetClass.FII, AssetClass.BDR)

VERBS_UP = ("sobe", "avança")
VERBS_UP_BIG = ("sobe", "salta", "dispara")
VERBS_DOWN = ("cai", "recua")
VERBS_DOWN_BIG = ("cai", "recua", "despenca")


def _before(market: MarketDay, quote: Quote) -> Sequence[float]:
    return market.closes.get(quote.ticker, ())


def _verb(change: float, *seed: object) -> str:
    big = abs(change) > BIG_MOVE
    if change > 0:
        return pick(VERBS_UP_BIG if big else VERBS_UP, *seed)
    return pick(VERBS_DOWN_BIG if big else VERBS_DOWN, *seed)


def strong_moves(market: MarketDay) -> list[Headline]:
    """Os ativos que subiram ou caíram mais que o limite contra o fechamento anterior, com a causa."""
    moves: list[tuple[float, Quote]] = []
    for quote in market.quotes:
        closes = _before(market, quote)
        if quote.asset_class not in MOVER_CLASSES or not closes or closes[-1] <= 0:
            continue
        change = quote.close / closes[-1] - 1
        if abs(change) > MOVE_THRESHOLD:
            moves.append((change, quote))
    moves.sort(key=lambda move: abs(move[0]), reverse=True)

    headlines = []
    for change, quote in moves[:MAX_PER_DAY]:
        rising = change > 0
        seed = (market.simulation_id, market.day, quote.ticker)
        name = short_name(quote.name, quote.ticker)
        cause = cause_for(quote.sector, rising, *seed)
        headlines.append(
            Headline(
                NewsType.STRONG_MOVE,
                f"{name} {_verb(change, *seed)} {number(abs(change) * 100, 1)}%",
                f"{quote.ticker} fecha a {price(quote.close)}. "
                f"O mercado atribui {'a alta' if rising else 'a queda'} a {cause}.",
                (quote.ticker,),
            )
        )
    return headlines


def week_highs(market: MarketDay) -> list[Headline]:
    """Os ativos que fecham acima de tudo o que fecharam nas últimas 52 semanas."""
    highs: list[tuple[float, Quote]] = []
    for quote in market.quotes:
        closes = _before(market, quote)[-YEAR_SESSIONS:]
        if len(closes) < MIN_SESSIONS:
            continue
        top = max(closes)
        if quote.close > top > 0:
            highs.append((quote.close / top - 1, quote))
    highs.sort(key=lambda high: high[0], reverse=True)

    headlines = []
    for margin, quote in highs[:MAX_PER_DAY]:
        name = short_name(quote.name, quote.ticker)
        text = pick(
            (
                f"{name} atinge o maior preço em um ano",
                f"{name} renova a máxima de 52 semanas",
            ),
            market.simulation_id,
            market.day,
            quote.ticker,
        )
        headlines.append(
            Headline(
                NewsType.WEEK_HIGH,
                text,
                f"{quote.ticker} fecha a {price(quote.close)}, "
                f"{number(margin * 100, 1)}% acima da máxima anterior.",
                (quote.ticker,),
            )
        )
    return headlines
