"""As manchetes das empresas: movimento forte para o ativo e rompimento da máxima de 52 semanas."""

from collections.abc import Sequence
from itertools import pairwise

from backend.core.enum import AssetClass, NewsType
from backend.core.periods import BUSINESS_DAYS_PER_YEAR
from backend.features.newsroom.causes import cause_for
from backend.features.newsroom.market import MarketDay, Quote
from backend.features.newsroom.text import number, pick, price, short_name
from backend.features.notifications.news import Headline

# Variação do dia, em fração, que vale para o ativo sem histórico suficiente para
# conhecer a própria oscilação
MOVE_THRESHOLD = 0.05
# Quantas vezes a oscilação normal do ativo a variação do dia precisa ter para virar manchete
MOVE_MULTIPLE = 4
# Piso absoluto: um ativo quase parado não vira manchete com 1%
MOVE_FLOOR = 0.03
# Os pregões que medem a oscilação normal e o mínimo deles para confiar na medida
NORMAL_MOVE_WINDOW = 126
MIN_NORMAL_SESSIONS = 63
# Acima deste tamanho o verbo sobe de tom: "salta" no lugar de "avança"
BIG_MOVE = 0.08
# Quantos ativos uma regra põe no jornal por pregão: o resto da rajada fica de fora
MAX_PER_DAY = 3
# O mínimo de histórico para chamar de máxima de 52 semanas
MIN_SESSIONS = 126
# A máxima rompida precisa ter pelo menos 3 meses de idade: quem sobe todo dia renova a
# máxima de ontem, e isso não é rompimento
MIN_HIGH_AGE = 63
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


def _normal_move(closes: Sequence[float]) -> float:
    """O tamanho médio da variação diária (em módulo, em fração) nos últimos pregões do ativo."""
    if len(closes) < MIN_NORMAL_SESSIONS:
        # Sem histórico para medir, o limite fixo vale: K vezes esta oscilação dá MOVE_THRESHOLD
        return MOVE_THRESHOLD / MOVE_MULTIPLE
    window = closes[-(NORMAL_MOVE_WINDOW + 1) :]
    changes = [abs(b / a - 1) for a, b in pairwise(window) if a > 0]
    return sum(changes) / len(changes) if changes else 0.0


def strong_moves(market: MarketDay) -> list[Headline]:
    """Os ativos que mexeram ao menos K vezes a própria oscilação normal contra o fechamento anterior, com a causa."""
    moves: list[tuple[float, float, Quote]] = []
    for quote in market.quotes:
        closes = _before(market, quote)
        if quote.asset_class not in MOVER_CLASSES or not closes or closes[-1] <= 0:
            continue
        change = quote.close / closes[-1] - 1
        normal = _normal_move(closes)
        if abs(change) >= max(MOVE_FLOOR, MOVE_MULTIPLE * normal):
            # A ordem do pregão é por quantas vezes a oscilação normal o ativo mexeu
            times = abs(change) / normal if normal > 0 else float("inf")
            moves.append((times, change, quote))
    moves.sort(key=lambda move: move[0], reverse=True)

    headlines = []
    for _, change, quote in moves[:MAX_PER_DAY]:
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
                round(change * 100, 2),
            )
        )
    return headlines


def week_highs(market: MarketDay) -> list[Headline]:
    """Os ativos que rompem uma máxima de 52 semanas com pelo menos 3 meses de idade."""
    highs: list[tuple[float, float, Quote]] = []
    for quote in market.quotes:
        closes = _before(market, quote)[-BUSINESS_DAYS_PER_YEAR:]
        if len(closes) < MIN_SESSIONS:
            continue
        top = max(closes)
        # Pregões desde que a máxima foi feita, contando o de hoje
        age = len(closes) - max(i for i, close in enumerate(closes) if close == top)
        if quote.close > top > 0 and closes[-1] > 0 and age >= MIN_HIGH_AGE:
            highs.append((quote.close / top - 1, quote.close / closes[-1] - 1, quote))
    highs.sort(key=lambda high: high[0], reverse=True)

    headlines = []
    for margin, change, quote in highs[:MAX_PER_DAY]:
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
                round(change * 100, 2),
            )
        )
    return headlines
