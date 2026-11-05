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
from backend.core.utils import last_day_of_month

ZERO = Decimal(0)
HUNDRED = Decimal(100)

# Crescimento da tendência (0.02 = 2% ao ano)
TREND = Decimal("0.02")
# Cada ponto de juro real acima do neutro tira 0,4 ponto do alvo de crescimento
NEUTRAL_REAL_RATE = Decimal("0.05")
REAL_RATE_WEIGHT = Decimal("0.4")
# Cada 10 pontos de alta do Ibovespa em 12 meses acima de 5% somam meio ponto ao alvo
NEUTRAL_STOCKS = Decimal("0.05")
STOCKS_WEIGHT = Decimal("0.05")
# O crescimento anda 1/4 do caminho até o alvo a cada fechamento, dentro da faixa
# que o PIB do Brasil já viu (de -4% em 1990 a +7,5% em 2010) com folga
GROWTH_STEP = Decimal("0.25")
MIN_GROWTH = Decimal("-0.06")
MAX_GROWTH = Decimal("0.08")
# Lei de Okun: cada ponto de crescimento acima da tendência baixa o desemprego em meio ponto ao ano
OKUN = Decimal("0.5")
NEUTRAL_UNEMPLOYMENT = Decimal("0.09")
MIN_UNEMPLOYMENT = Decimal("0.04")
MAX_UNEMPLOYMENT = Decimal("0.18")
MONTHS_PER_YEAR = Decimal(12)
STOCKS_WINDOW_DAYS = 365

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
    # Alta do Ibovespa em 12 meses (nula quando a série não cobre) e o quanto ela empurra
    stocks: Decimal | None
    stocks_part: Decimal
    # O que as obras do governo somam ao alvo, em fração ao ano
    spending_part: Decimal = ZERO
    # O que o resultado primário do governo, fora as obras, soma ao alvo
    impulse_part: Decimal = ZERO

    @property
    def value(self) -> Decimal:
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

    @property
    def total(self) -> Decimal:
        return self.real_rate + self.stocks + self.spending + self.impulse

    def toward(self, game: GrowthAim, base: GrowthAim) -> "GrowthGap":
        def step(part: Decimal, aim: Decimal) -> Decimal:
            return part + GROWTH_STEP * (aim - part)

        return GrowthGap(
            real_rate=step(self.real_rate, game.real_rate_part - base.real_rate_part),
            stocks=step(self.stocks, game.stocks_part - base.stocks_part),
            spending=step(self.spending, game.spending_part),
            impulse=step(self.impulse, game.impulse_part),
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


def growth_aim(
    day: date,
    spending: Decimal = ZERO,
    impulse: Decimal = ZERO,
    *,
    stored: bool = False,
) -> GrowthAim:
    """
    O alvo do crescimento com o que o jogador conhece em `day`, mais o que as obras e o
    resultado primário somam; com `stored`, o alvo da história, pelas séries guardadas.
    """
    real_rate = annual_index_rate(
        IndicatorSeries.SELIC, day, stored=stored
    ) - annual_index_rate(IndicatorSeries.IPCA, day, stored=stored)
    now = last_known_value(IndicatorSeries.IBOV, day, stored=stored)
    before = last_known_value(
        IndicatorSeries.IBOV, day - timedelta(days=STOCKS_WINDOW_DAYS), stored=stored
    )
    stocks = now / before - 1 if now is not None and before else None
    return GrowthAim(
        trend=TREND,
        real_rate=real_rate,
        real_rate_part=-REAL_RATE_WEIGHT * (real_rate - NEUTRAL_REAL_RATE),
        stocks=stocks,
        # Sem série de bolsa, a bolsa fica no neutro: não empurra nem puxa
        stocks_part=(
            STOCKS_WEIGHT * (stocks - NEUTRAL_STOCKS) if stocks is not None else ZERO
        ),
        spending_part=spending,
        impulse_part=impulse,
    )


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
    )


def next_month(
    previous: MacroMonth,
    month_end: date,
    spending: Decimal = ZERO,
    impulse: Decimal = ZERO,
) -> MacroMonth:
    """
    O fechamento seguinte. A base é a série guardada; onde ela não cobre, o modelo anda
    1/4 até o alvo da história e o desemprego segue o Okun. A partida soma à base o
    desvio de cada parte do alvo, e o desvio do desemprego segue o Okun sobre o desvio
    do crescimento.
    """
    base_aim = growth_aim(month_end, stored=True)
    base_growth = recorded_growth(month_end)
    if base_growth is None:
        base_growth = clamp(
            previous.base_growth
            + GROWTH_STEP * (base_aim.value - previous.base_growth),
            MIN_GROWTH,
            MAX_GROWTH,
        )
    base_unemployment = recorded_unemployment(month_end)
    if base_unemployment is None:
        base_unemployment = clamp(
            previous.base_unemployment - OKUN * (base_growth - TREND) / MONTHS_PER_YEAR,
            MIN_UNEMPLOYMENT,
            MAX_UNEMPLOYMENT,
        )

    # A faixa vale para o desvio: a história fica como foi, mesmo fora dela
    aim = growth_aim(month_end, spending, impulse)
    gap = previous.gap.toward(aim, base_aim)
    growth = clamp(
        base_growth + gap.total,
        min(MIN_GROWTH, base_growth),
        max(MAX_GROWTH, base_growth),
    )
    unemployment_gap = (
        previous.unemployment
        - previous.base_unemployment
        - OKUN * (growth - base_growth) / MONTHS_PER_YEAR
    )
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

    def use_government(self, spending: GrowthSource, impulse: GrowthSource) -> None:
        """O que as obras e o resultado primário do governo somam ao alvo do crescimento em cada dia."""
        self._spending_on = spending
        self._impulse_on = impulse

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
                    )
                )
            return [m for m in self._months if m.month_end <= day]

    def latest(self, day: date) -> MacroMonth:
        """O último mês fechado em `day`; antes do primeiro, o ponto de partida."""
        closed = self.months_until(day)
        return closed[-1] if closed else self._initial
