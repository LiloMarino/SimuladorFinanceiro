"""
Crescimento e desemprego do país, mês a mês, em duas linhas. A linha de base é a
história: o PIB e o desemprego das séries guardadas e, onde elas não cobrem, o modelo
(o alvo do crescimento sai da SELIC, do IPCA e do Ibovespa guardados, e o desemprego
segue o crescimento pela lei de Okun). A partida é a base mais o desvio que o governo
causa: cada parte do alvo da partida que difere da base empurra o crescimento pelo
mesmo passo do modelo. Sem governo as duas linhas coincidem. O curso avança um
fechamento de mês por vez e guarda o que já andou: um mês fechado nunca muda.
"""

import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from backend.core import repository
from backend.core.enum import IndicatorSeries
from backend.core.indicators import annual_index_rate, last_known_value
from backend.core.periods import MONTHS_PER_YEAR
from backend.core.utils import last_day_of_month

ZERO = Decimal(0)
ONE = Decimal(1)
HUNDRED = Decimal(100)

# Crescimento da tendência (0.02 = 2% ao ano)
TREND = Decimal("0.02")
# Cada ponto de juro real acima do neutro tira 0,4 ponto do alvo de crescimento
NEUTRAL_REAL_RATE = Decimal("0.05")
REAL_RATE_WEIGHT = Decimal("0.4")
# Cada 10 pontos de alta do Ibovespa em 12 meses, descontada a inflação, acima de 5%
# somam meio ponto ao alvo
NEUTRAL_STOCKS = Decimal("0.05")
STOCKS_WEIGHT = Decimal("0.05")
# O crescimento anda 1/4 do caminho até o alvo a cada fechamento, dentro da faixa
# que o PIB do Brasil já viu (de -4% em 1990 a +7,5% em 2010) com folga
GROWTH_STEP = Decimal("0.25")
MIN_GROWTH = Decimal("-0.06")
MAX_GROWTH = Decimal("0.08")
# O desvio do governo derruba o crescimento da partida até -15% ao ano; para cima não há
# teto. O ciclo crescimento → dívida ÷ PIB → prêmio → crescimento só fecha com números
# finitos com esse piso (o PIB nunca chega a -100%, onde a dívida ÷ PIB deixa de ter valor)
COLLAPSE_GROWTH = Decimal("-0.15")
# Lei de Okun: cada ponto de crescimento acima da tendência baixa o desemprego em meio ponto ao ano
OKUN = Decimal("0.5")
NEUTRAL_UNEMPLOYMENT = Decimal("0.09")
MIN_UNEMPLOYMENT = Decimal("0.04")
MAX_UNEMPLOYMENT = Decimal("0.18")
# O desvio do desemprego contra a história cai pela metade a cada 36 meses: o normal da
# época é a taxa para a qual o país volta, devagar, quando a economia sai do aquecimento
# ou da recessão. O fator mensal é a raiz 36 de 1/2.
UNEMPLOYMENT_HALF_LIFE_MONTHS = 36
UNEMPLOYMENT_RETURN = Decimal("0.5") ** (Decimal(1) / UNEMPLOYMENT_HALF_LIFE_MONTHS)
STOCKS_WINDOW_DAYS = 365
# Inflação alta tira crescimento: o IPCA de 12 meses acima de 12% ao ano tira 1,2 ponto do
# alvo a cada ponto acima do limiar (Khan e Senhadji, 2001); abaixo dele, nada
INFLATION_THRESHOLD = Decimal("0.12")
INFLATION_WEIGHT = Decimal("1.2")
# Paridade do poder de compra: onde a PTAX guardada não cobre, o dólar da história sobe ao
# ano a diferença entre o IPCA da história e a inflação dos EUA
US_INFLATION = Decimal("0.025")

GrowthSource = Callable[[date], Decimal]


def no_push(_day: date) -> Decimal:
    return ZERO


def clamp(value: Decimal, low: Decimal, high: Decimal) -> Decimal:
    return max(low, min(high, value))


@dataclass(frozen=True)
class GrowthAim:
    """Onde o crescimento para se nada mudar, e o que o puxa até lá (frações ao ano)."""

    trend: Decimal
    # Juro real do dia (SELIC menos IPCA) e o quanto ele empurra o alvo
    real_rate: Decimal
    real_rate_part: Decimal
    # Alta do Ibovespa em 12 meses descontado o IPCA (nula quando a série não cobre) e o
    # quanto ela empurra
    stocks: Decimal | None
    stocks_part: Decimal
    # O que as obras do governo somam ao alvo, em fração ao ano
    spending_part: Decimal = ZERO
    # O que o resultado primário do governo, fora as obras, soma ao alvo
    impulse_part: Decimal = ZERO
    # O IPCA de 12 meses e o que a parte acima do limiar tira do alvo
    inflation: Decimal = ZERO
    inflation_part: Decimal = ZERO
    # O que o prêmio de risco acima da história tira do alvo, pelo crédito mais caro
    crowding_part: Decimal = ZERO

    @property
    def value(self) -> Decimal:
        """
        O alvo do modelo da história: a tendência, o juro real, a bolsa, as obras e o
        impulso. A inflação alta e o crédito caro são desvios contra a história e agem
        só pelo `GrowthGap`.
        """
        return (
            self.trend
            + self.real_rate_part
            + self.stocks_part
            + self.spending_part
            + self.impulse_part
        )


@dataclass(frozen=True)
class GrowthGap:
    """
    O que a partida soma ao crescimento da história, por causa, em fração ao ano. Cada
    parte anda 1/4 do caminho até a diferença entre o alvo da partida e o da base, então
    a soma das partes é o desvio que o modelo daria.
    """

    real_rate: Decimal = ZERO
    stocks: Decimal = ZERO
    spending: Decimal = ZERO
    impulse: Decimal = ZERO
    inflation: Decimal = ZERO
    crowding: Decimal = ZERO

    @property
    def total(self) -> Decimal:
        return (
            self.real_rate
            + self.stocks
            + self.spending
            + self.impulse
            + self.inflation
            + self.crowding
        )

    def toward(self, game: GrowthAim, base: GrowthAim) -> "GrowthGap":
        def step(part: Decimal, aim: Decimal) -> Decimal:
            return part + GROWTH_STEP * (aim - part)

        return GrowthGap(
            real_rate=step(self.real_rate, game.real_rate_part - base.real_rate_part),
            stocks=step(self.stocks, game.stocks_part - base.stocks_part),
            spending=step(self.spending, game.spending_part),
            impulse=step(self.impulse, game.impulse_part),
            inflation=step(self.inflation, game.inflation_part - base.inflation_part),
            crowding=step(self.crowding, game.crowding_part),
        )


@dataclass(frozen=True)
class MacroMonth:
    """
    O país no fim de um mês: o crescimento e o desemprego da partida, com o alvo que os
    moveu, e os da linha de base (a história) de que a partida se desvia.
    """

    month_end: date
    # Crescimento em 12 meses e desemprego da partida, em fração (0.022 e 0.116)
    growth: Decimal
    unemployment: Decimal
    aim: GrowthAim
    base_growth: Decimal
    base_unemployment: Decimal
    base_aim: GrowthAim
    gap: GrowthGap = GrowthGap()
    # O dólar da história em reais no fim do mês: a PTAX guardada ou, sem cobertura, a paridade
    base_dollar: Decimal = ONE


def aim_from(
    selic: Decimal,
    inflation: Decimal,
    stocks: Decimal | None,
    spending: Decimal = ZERO,
    impulse: Decimal = ZERO,
    crowding: Decimal = ZERO,
) -> GrowthAim:
    """
    O alvo do crescimento para a SELIC, o IPCA de 12 meses e a alta nominal do Ibovespa em
    12 meses dados (frações ao ano), mais o que as obras, o resultado primário e o crédito
    caro somam. O juro e a bolsa entram descontada a inflação, então inflação que só infla
    os preços não mexe neles; só a parte do IPCA acima do limiar tira crescimento. Sem
    série de bolsa, a bolsa fica no neutro: não empurra nem puxa.
    """
    real_rate = selic - inflation
    inflation_part = -INFLATION_WEIGHT * max(ZERO, inflation - INFLATION_THRESHOLD)
    if stocks is not None:
        stocks = (1 + stocks) / (1 + inflation) - 1
    return GrowthAim(
        trend=TREND,
        real_rate=real_rate,
        real_rate_part=-REAL_RATE_WEIGHT * (real_rate - NEUTRAL_REAL_RATE),
        stocks=stocks,
        stocks_part=(
            STOCKS_WEIGHT * (stocks - NEUTRAL_STOCKS) if stocks is not None else ZERO
        ),
        spending_part=spending,
        impulse_part=impulse,
        inflation=inflation,
        inflation_part=inflation_part,
        crowding_part=crowding,
    )


def growth_aim(
    day: date,
    spending: Decimal = ZERO,
    impulse: Decimal = ZERO,
    crowding: Decimal = ZERO,
    *,
    stored: bool = False,
) -> GrowthAim:
    """
    O alvo do crescimento com o que o jogador conhece em `day`, mais o que as obras, o
    resultado primário e o crédito caro somam; com `stored`, o alvo da história, pelas
    séries guardadas.
    """
    now = last_known_value(IndicatorSeries.IBOV, day, stored=stored)
    before = last_known_value(
        IndicatorSeries.IBOV, day - timedelta(days=STOCKS_WINDOW_DAYS), stored=stored
    )
    return aim_from(
        annual_index_rate(IndicatorSeries.SELIC, day, stored=stored),
        annual_index_rate(IndicatorSeries.IPCA, day, stored=stored),
        now / before - 1 if now is not None and before else None,
        spending,
        impulse,
        crowding,
    )


def step_growth(previous: Decimal, aim_value: Decimal) -> Decimal:
    """O crescimento anda 1/4 do caminho até o alvo, dentro da faixa."""
    return clamp(
        previous + GROWTH_STEP * (aim_value - previous), MIN_GROWTH, MAX_GROWTH
    )


def step_unemployment(previous: Decimal, growth: Decimal) -> Decimal:
    """O desemprego segue o crescimento do mês pela lei de Okun, dentro da faixa."""
    return clamp(
        previous - OKUN * (growth - TREND) / MONTHS_PER_YEAR,
        MIN_UNEMPLOYMENT,
        MAX_UNEMPLOYMENT,
    )


def step_dollar(previous: Decimal, inflation: Decimal) -> Decimal:
    """O dólar da história sobe, a cada mês, um doze avos da diferença entre o IPCA e a inflação dos EUA."""
    return previous * (1 + (inflation - US_INFLATION) / MONTHS_PER_YEAR)


def recorded_dollar(month_end: date) -> Decimal | None:
    """A PTAX do último pregão guardado até o fechamento; nula antes da série e depois do último dado real."""
    history = repository.economic.get_history(IndicatorSeries.PTAX, stored=True)
    if history.end is None or history.end < month_end.replace(day=1):
        return None
    return history.last_known(month_end)


def quarter_start(day: date) -> date:
    return date(day.year, 3 * ((day.month - 1) // 3) + 1, 1)


def recorded(series: IndicatorSeries, day: date) -> Decimal | None:
    """O valor guardado da série exatamente em `day`, em fração; nulo fora da cobertura."""
    value = repository.economic.get_history(series, stored=True).value_on(day)
    return None if value is None else value / HUNDRED


def recorded_growth(month_end: date) -> Decimal | None:
    """O PIB vem por trimestre, datado no primeiro dia do trimestre que fecha a conta."""
    return recorded(IndicatorSeries.GDP_GROWTH, quarter_start(month_end))


def recorded_unemployment(month_end: date) -> Decimal | None:
    return recorded(IndicatorSeries.UNEMPLOYMENT, month_end.replace(day=1))


def starting_month(day: date) -> MacroMonth:
    """O país antes do primeiro fechamento: a história do dia, ou a tendência e o desemprego neutro onde ela não cobre."""
    growth = recorded_growth(day)
    unemployment = recorded_unemployment(day)
    base_growth = TREND if growth is None else growth
    base_unemployment = NEUTRAL_UNEMPLOYMENT if unemployment is None else unemployment
    return MacroMonth(
        month_end=day,
        growth=base_growth,
        unemployment=base_unemployment,
        aim=growth_aim(day),
        base_growth=base_growth,
        base_unemployment=base_unemployment,
        base_aim=growth_aim(day, stored=True),
        base_dollar=recorded_dollar(day) or ONE,
    )


def next_month(
    previous: MacroMonth,
    month_end: date,
    spending: Decimal = ZERO,
    impulse: Decimal = ZERO,
    crowding: Decimal = ZERO,
    payroll: Decimal = ZERO,
) -> MacroMonth:
    """
    O fechamento seguinte. A base é a série guardada; onde ela não cobre, o modelo anda
    1/4 até o alvo da história e o desemprego segue o Okun. A partida soma à base o
    desvio de cada parte do alvo, sem faixa: quem segura o crescimento são o juro, a
    inflação e o crédito, cada um com a sua parcela. O desvio do desemprego volta
    devagar a zero e segue o Okun sobre o desvio do crescimento, mais o que a contribuição
    sobre a folha soma ao ano (`payroll`).
    """
    base_aim = growth_aim(month_end, stored=True)
    base_growth = recorded_growth(month_end)
    if base_growth is None:
        base_growth = step_growth(previous.base_growth, base_aim.value)
    base_unemployment = recorded_unemployment(month_end)
    if base_unemployment is None:
        base_unemployment = step_unemployment(previous.base_unemployment, base_growth)

    base_dollar = recorded_dollar(month_end)
    if base_dollar is None:
        base_dollar = step_dollar(previous.base_dollar, base_aim.inflation)

    aim = growth_aim(month_end, spending, impulse, crowding)
    gap = previous.gap.toward(aim, base_aim)
    growth = max(COLLAPSE_GROWTH, base_growth + gap.total)
    unemployment_gap = (
        previous.unemployment - previous.base_unemployment
    ) * UNEMPLOYMENT_RETURN + (
        payroll - OKUN * (growth - base_growth)
    ) / MONTHS_PER_YEAR
    return MacroMonth(
        month_end=month_end,
        growth=growth,
        unemployment=clamp(
            base_unemployment + unemployment_gap,
            min(MIN_UNEMPLOYMENT, base_unemployment),
            max(MAX_UNEMPLOYMENT, base_unemployment),
        ),
        aim=aim,
        base_growth=base_growth,
        base_unemployment=base_unemployment,
        base_aim=base_aim,
        gap=gap,
        base_dollar=base_dollar,
    )


class MacroCourse:
    """
    Os fechamentos de mês da economia desde o começo da partida. O cálculo avança só até
    o dia consultado e refaz tudo desde o início numa retomada, como o replay do governo.
    """

    def __init__(self, start: date):
        self._lock = threading.Lock()
        self._initial = starting_month(start - timedelta(days=1))
        self._months: list[MacroMonth] = []
        self._spending_on: GrowthSource = no_push
        self._impulse_on: GrowthSource = no_push
        self._crowding_on: GrowthSource = no_push
        self._payroll_on: GrowthSource = no_push

    def use_government(
        self,
        spending: GrowthSource,
        impulse: GrowthSource,
        crowding: GrowthSource = no_push,
        payroll: GrowthSource = no_push,
    ) -> None:
        """O que o gasto, o resultado primário e o crédito caro do governo somam ao alvo do crescimento em cada dia, e o que a folha mais cara soma ao desemprego ao ano."""
        self._spending_on = spending
        self._impulse_on = impulse
        self._crowding_on = crowding
        self._payroll_on = payroll

    def months_until(self, day: date) -> list[MacroMonth]:
        """Os meses já fechados em `day`: o fim do mês é hoje ou já passou."""
        with self._lock:
            while True:
                last = self._months[-1] if self._months else self._initial
                following = last_day_of_month(last.month_end + timedelta(days=1))
                if following > day:
                    break
                self._months.append(
                    next_month(
                        last,
                        following,
                        self._spending_on(following),
                        self._impulse_on(following),
                        self._crowding_on(following),
                        self._payroll_on(following),
                    )
                )
            return [m for m in self._months if m.month_end <= day]

    def latest(self, day: date) -> MacroMonth:
        """O último mês fechado em `day`; antes do primeiro, o ponto de partida."""
        closed = self.months_until(day)
        return closed[-1] if closed else self._initial


def history_dollar(day: date, macro: MacroCourse) -> Decimal:
    """O dólar da história em `day`: a PTAX guardada até o último dado real e, depois, o do último mês fechado, pela paridade."""
    return recorded_dollar(day) or macro.latest(day).base_dollar
