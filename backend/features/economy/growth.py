"""
Crescimento e desemprego do país, mês a mês. O alvo do crescimento sai de três coisas
que as séries já guardam (SELIC, IPCA e Ibovespa), então vale igual na história real e
no futuro gerado; o desemprego segue o crescimento pela lei de Okun. O curso avança
um fechamento de mês por vez e guarda o que já andou: um mês fechado nunca muda.
"""

import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from backend.core.enum import IndicatorSeries
from backend.core.indicators import annual_index_rate, last_known_value
from backend.core.utils import last_day_of_month

# Crescimento da tendência (0.02 = 2% ao ano)
TREND = Decimal("0.02")
# Cada ponto de juro real acima do neutro tira 0,4 ponto do alvo de crescimento
NEUTRAL_REAL_RATE = Decimal("0.05")
REAL_RATE_WEIGHT = Decimal("0.4")
# Cada ponto de alta do Ibovespa em 12 meses acima de 5% soma 5 pontos ao alvo
NEUTRAL_STOCKS = Decimal("0.05")
STOCKS_WEIGHT = Decimal(5)
# O crescimento anda 1/4 do caminho até o alvo a cada fechamento
GROWTH_STEP = Decimal("0.25")
# Lei de Okun: cada ponto de crescimento acima da tendência baixa o desemprego em meio ponto ao ano
OKUN = Decimal("0.5")
NEUTRAL_UNEMPLOYMENT = Decimal("0.09")
MIN_UNEMPLOYMENT = Decimal("0.04")
MAX_UNEMPLOYMENT = Decimal("0.18")
MONTHS_PER_YEAR = Decimal(12)
STOCKS_WINDOW_DAYS = 365


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
    spending_part: Decimal = Decimal(0)

    @property
    def value(self) -> Decimal:
        return self.trend + self.real_rate_part + self.stocks_part + self.spending_part


@dataclass(frozen=True)
class MacroMonth:
    """O país no fim de um mês: crescimento e desemprego, com o alvo que moveu o crescimento."""

    month_end: date
    # Crescimento em 12 meses e desemprego, em fração (0.022 e 0.116)
    growth: Decimal
    unemployment: Decimal
    aim: GrowthAim


def growth_aim(day: date, spending: Decimal = Decimal(0)) -> GrowthAim:
    """O alvo do crescimento com o que o jogador conhece em `day`, mais o que as obras somam."""
    real_rate = annual_index_rate(IndicatorSeries.SELIC, day) - annual_index_rate(
        IndicatorSeries.IPCA, day
    )
    now = last_known_value(IndicatorSeries.IBOV, day)
    before = last_known_value(
        IndicatorSeries.IBOV, day - timedelta(days=STOCKS_WINDOW_DAYS)
    )
    stocks = now / before - 1 if now is not None and before else None
    return GrowthAim(
        trend=TREND,
        real_rate=real_rate,
        real_rate_part=-REAL_RATE_WEIGHT * (real_rate - NEUTRAL_REAL_RATE),
        stocks=stocks,
        # Sem série de bolsa, a bolsa fica no neutro: não empurra nem puxa
        stocks_part=(
            STOCKS_WEIGHT * (stocks - NEUTRAL_STOCKS)
            if stocks is not None
            else Decimal(0)
        ),
        spending_part=spending,
    )


def next_month(
    previous: MacroMonth, month_end: date, spending: Decimal = Decimal(0)
) -> MacroMonth:
    """O fechamento seguinte: o crescimento anda 1/4 até o alvo e o desemprego segue o Okun."""
    aim = growth_aim(month_end, spending)
    growth = previous.growth + GROWTH_STEP * (aim.value - previous.growth)
    unemployment = previous.unemployment - OKUN * (growth - TREND) / MONTHS_PER_YEAR
    return MacroMonth(
        month_end=month_end,
        growth=growth,
        unemployment=max(MIN_UNEMPLOYMENT, min(MAX_UNEMPLOYMENT, unemployment)),
        aim=aim,
    )


class MacroCourse:
    """
    Os fechamentos de mês da economia desde o começo da partida. O cálculo avança só até
    o dia consultado e refaz tudo desde o início numa retomada, como o replay do governo.
    """

    def __init__(self, start: date):
        self._start = start
        self._lock = threading.Lock()
        # O estado de antes do primeiro fechamento: na tendência e no desemprego neutro
        self._initial = MacroMonth(
            month_end=start - timedelta(days=1),
            growth=TREND,
            unemployment=NEUTRAL_UNEMPLOYMENT,
            aim=growth_aim(start - timedelta(days=1)),
        )
        self._months: list[MacroMonth] = []
        self._spending_on: Callable[[date], Decimal] = lambda _day: Decimal(0)

    def use_spending(self, source: Callable[[date], Decimal]) -> None:
        """O que as obras do governo somam ao alvo do crescimento em cada dia."""
        self._spending_on = source

    def months_until(self, day: date) -> list[MacroMonth]:
        """Os meses já fechados em `day`: o fim do mês é hoje ou já passou."""
        with self._lock:
            while True:
                last = self._months[-1] if self._months else self._initial
                following = last_day_of_month(last.month_end + timedelta(days=1))
                if following > day:
                    break
                self._months.append(
                    next_month(last, following, self._spending_on(following))
                )
            return [m for m in self._months if m.month_end <= day]

    def latest(self, day: date) -> MacroMonth:
        """O último mês fechado em `day`; antes do primeiro, o ponto de partida."""
        closed = self.months_until(day)
        return closed[-1] if closed else self._initial
