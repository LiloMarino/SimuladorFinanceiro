"""
As regras do Corretor: a comissão sobre o volume da sala e o relatório mensal da casa,
em Decimal e sem estado. O relatório sai do futuro já guardado no banco mais um sorteio
calibrado; nenhum preço futuro sai daqui, só o alvo e o prazo.
"""

import random
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from backend.core.clt import cents
from backend.core.dates import add_months
from backend.core.enum import HouseResult, OrderAction
from backend.core.utils import is_business_day, last_day_of_month

# A comissão é esta fração do volume negociado na sala no mês, dividida entre os Corretores
COMMISSION_RATE = Decimal("0.0005")
# A comissão de cada Corretor vale no máximo este múltiplo da parte fixa; o excedente fica com a casa
COMMISSION_CAP = Decimal(1)

# O relatório sai neste dia útil do mês, contado do dia 1
REPORT_BUSINESS_DAY = 5
# Quantas ações cada relatório traz
MIN_PICKS = 3
MAX_PICKS = 5
# O prazo de cada recomendação é o fim de um mês entre estes, contados do mês do relatório
MIN_HORIZON_MONTHS = 1
MAX_HORIZON_MONTHS = 3

# Política do bot: a fração do patrimônio que vai às recomendações de compra do dia
BOT_BUDGET_SHARE = Decimal("0.2")

# A chance de a casa recomendar o lado em que o preço de fato anda dentro do prazo
HOUSE_ACCURACY = 0.62
# A ação cujo movimento favorável no prazo é menor que isto não entra no relatório
MIN_REACH = 0.04
# Quando a casa lê certo, o alvo fica nesta faixa do movimento que o preço faz até o prazo
TARGET_SHARE_MIN = 0.5
TARGET_SHARE_MAX = 0.9
# Quando lê errado, o alvo passa do movimento do lado recomendado por esta folga
MISS_MARGIN = 1.1
MISS_EXTRA = 0.01


@dataclass(frozen=True)
class Commission:
    """A comissão de um Corretor no mês: o valor depois do teto e o que a regra pagaria sem ele."""

    amount: Decimal
    uncapped: Decimal

    @property
    def capped(self) -> bool:
        return self.uncapped > self.amount


def commission(volume: Decimal, brokers: int, fixed: Decimal) -> Commission:
    """A parte de cada Corretor: a fração do volume dividida em partes iguais, até o teto sobre a parte fixa."""
    if brokers <= 0 or volume <= 0:
        return Commission(Decimal(0), Decimal(0))
    share = cents(volume * COMMISSION_RATE / brokers)
    return Commission(min(share, cents(fixed * COMMISSION_CAP)), share)


def previous_month_start(day: date) -> date:
    """O dia 1 do mês anterior ao de `day`."""
    return (day.replace(day=1) - timedelta(days=1)).replace(day=1)


def report_day(month: date) -> date:
    """O dia em que o relatório do mês de `month` sai: o 5º dia útil."""
    day = month.replace(day=1)
    count = 0
    while True:
        if is_business_day(day):
            count += 1
            if count == REPORT_BUSINESS_DAY:
                return day
        day += timedelta(days=1)


def next_report_on(day: date, issued_months: set[date]) -> date:
    """O dia do próximo relatório a partir de `day`: o do mês, se ainda não saiu e o dia não passou, ou o do mês seguinte."""
    month = day.replace(day=1)
    this_month = report_day(month)
    if month not in issued_months and day <= this_month:
        return this_month
    return report_day(add_months(month, 1))


def deadline_of(month: date, horizon: int, end_date: date) -> date:
    """O fim do mês `horizon` meses depois de `month`, sem passar do fim da partida."""
    return min(last_day_of_month(add_months(month.replace(day=1), horizon)), end_date)


def reached(side: OrderAction, target: Decimal, high: Decimal, low: Decimal) -> bool:
    """A compra acerta quando a máxima toca o alvo; a venda, quando a mínima toca."""
    return high >= target if side is OrderAction.BUY else low <= target


@dataclass(frozen=True)
class Draft:
    """Uma recomendação saída do sorteio."""

    ticker: str
    side: OrderAction
    price: Decimal
    target: Decimal
    deadline: date


@dataclass(frozen=True)
class Candidate:
    """Uma ação negociável no dia: o preço de hoje e a máxima e a mínima de cada pregão guardado até o maior prazo possível."""

    ticker: str
    price: Decimal
    future: Sequence[tuple[date, Decimal, Decimal]]


def _reach(
    price: Decimal, future: Sequence[tuple[date, Decimal, Decimal]]
) -> tuple[float, float]:
    """O quanto o preço chega acima e abaixo do de hoje nos pregões dados, em fração."""
    high = max(h for _, h, _ in future)
    low = min(lo for _, _, lo in future)
    return float(high / price - 1), float(1 - low / price)


def recommend(
    rng: random.Random,
    ticker: str,
    price: Decimal,
    reach_up: float,
    reach_down: float,
    deadline: date,
) -> Draft | None:
    """
    A recomendação da casa para uma ação, dado até onde o preço sobe e desce até o prazo.
    Com chance `HOUSE_ACCURACY` a casa lê o lado do maior movimento e põe o alvo dentro
    dele; no resto, recomenda o outro lado com o alvo além do que o preço chega ali.
    Movimento pequeno demais não gera recomendação.
    """
    right_reach = max(reach_up, reach_down)
    if right_reach < MIN_REACH:
        return None
    right_side = OrderAction.BUY if reach_up >= reach_down else OrderAction.SELL
    distance = right_reach * rng.uniform(TARGET_SHARE_MIN, TARGET_SHARE_MAX)
    if rng.random() < HOUSE_ACCURACY:
        side = right_side
    else:
        side = OrderAction.SELL if right_side is OrderAction.BUY else OrderAction.BUY
        wrong_reach = min(reach_up, reach_down)
        distance = max(distance, wrong_reach * MISS_MARGIN + MISS_EXTRA)
    sign = 1 if side is OrderAction.BUY else -1
    target = cents(price * (1 + sign * Decimal(str(round(distance, 6)))))
    return Draft(ticker, side, price, target, deadline)


def draw_report(
    seed: str,
    day: date,
    end_date: date,
    candidates: Sequence[Candidate],
) -> list[Draft]:
    """
    O relatório do mês de `day`: de 3 a 5 ações sorteadas entre `candidates`, cada uma
    com o prazo no fim de um dos próximos 1 a 3 meses. O sorteio é fixo para a mesma
    `seed` e o mesmo dia; ação sem movimento suficiente é trocada pela seguinte.
    """
    rng = random.Random(f"{seed}:{day.isoformat()}")
    wanted = rng.randint(MIN_PICKS, MAX_PICKS)
    order = list(candidates)
    rng.shuffle(order)
    picks: list[Draft] = []
    for candidate in order:
        if len(picks) == wanted:
            break
        horizon = rng.randint(MIN_HORIZON_MONTHS, MAX_HORIZON_MONTHS)
        deadline = deadline_of(day, horizon, end_date)
        window = [row for row in candidate.future if day < row[0] <= deadline]
        if not window or candidate.price <= 0:
            continue
        up, down = _reach(candidate.price, window)
        draft = recommend(rng, candidate.ticker, candidate.price, up, down, deadline)
        if draft is not None:
            picks.append(draft)
    return picks


@dataclass(frozen=True)
class Verdict:
    """O desfecho de uma recomendação num dia: o resultado e o preço que o placar mostra."""

    result: HouseResult
    price: Decimal


def judge(
    side: OrderAction,
    target: Decimal,
    deadline: date,
    next_day: date,
    high: Decimal,
    low: Decimal,
    close: Decimal,
) -> Verdict | None:
    """
    O desfecho da recomendação no pregão de hoje: acerta com a máxima (compra) ou a mínima
    (venda) que toca o alvo, e erra quando o prazo fecha sem tocar; antes disso segue
    em aberto. `next_day` é o pregão seguinte, que diz se hoje foi o último do prazo.
    """
    if reached(side, target, high, low):
        return Verdict(HouseResult.HIT, high if side is OrderAction.BUY else low)
    if next_day > deadline:
        return Verdict(HouseResult.MISS, close)
    return None


def hit_rate(hits: int, resolved: int) -> Decimal | None:
    """A fração de recomendações que acertaram entre as resolvidas; nulo sem nenhuma."""
    if resolved == 0:
        return None
    return Decimal(hits) / Decimal(resolved)
