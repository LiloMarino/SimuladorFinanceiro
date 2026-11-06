"""
A camada que a partida põe por cima das séries guardadas: IPCA, SELIC, CDI e Ibovespa
ganham o efeito das medidas de gasto e das ligações da economia, e cada ação ganha o
nível da bolsa elevado ao beta dela. A SELIC é a que o governo fixou na última reunião
ou, sem decisão, a reação do Banco Central autônomo à inflação a mais; a bolsa cai com
a SELIC e o prêmio de risco a mais e sobe com o PIB acima da história. As séries
guardadas seguem como estavam.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from itertools import pairwise
from typing import Protocol

from backend.core import repository
from backend.core.enum import IndicatorSeries
from backend.core.indicators import (
    BUSINESS_DAYS_PER_YEAR,
    annual_index_rate,
    annualize_daily,
)
from backend.core.repository.economic import IndicatorHistory
from backend.features.economy.links import NO_LINK, LinkMonth
from backend.features.economy.monetary import AutonomousBank, Monetary

DAYS_PER_MONTH = 30.4375
# A SELIC reage com 1,5 ponto por ponto de inflação a mais (Banco Central autônomo)
SELIC_REACTION = 1.5
# A bolsa cai 2,9% por ponto de alta da SELIC ou do prêmio de risco, espalhado pelo trimestre
STOCKS_PER_SELIC = 0.029
STOCKS_WINDOW_MONTHS = 3
# A bolsa sobe 2,5% por ponto de PIB acima da história
STOCKS_PER_GDP = 2.5

# Janela do histórico, antes do início da partida, que mede o beta de cada ativo contra o Ibovespa
BETA_WINDOW_DAYS = 730
MIN_BETA_DAYS = 60
MAX_BETA = 3.0


def central_bank_reaction(inflation_points: float) -> float:
    """Os pontos de SELIC que o Banco Central soma pelos pontos de IPCA a mais."""
    return SELIC_REACTION * inflation_points


def months_back(day: date, months: int) -> date:
    return day - timedelta(days=round(DAYS_PER_MONTH * months))


def quarter_mean(points: Callable[[date], float], day: date) -> float:
    """A média de `points` no dia e um e dois meses antes: o mercado leva o trimestre para absorver."""
    return (
        sum(points(months_back(day, back)) for back in range(STOCKS_WINDOW_MONTHS))
        / STOCKS_WINDOW_MONTHS
    )


def annual_to_daily(annual: float) -> float:
    """Taxa diária em % de uma taxa anual em fração composta por 252 dias úteis."""
    return ((1 + annual) ** (1 / BUSINESS_DAYS_PER_YEAR) - 1) * 100


@dataclass(frozen=True)
class StocksParts:
    """
    O nível da bolsa por causa, como expoente: o nível é e elevado à soma. Com o Banco
    Central autônomo, a SELIC que as medidas de gasto põem, a que a curva de Phillips
    põe, a que o juro real põe pela inflação dele e o risco fiscal (o prêmio e a SELIC
    que a inflação dele põe). Com a SELIC do governo, ela pesa inteira em `selic` e as
    outras partes ficam só com o que não é SELIC. Por fim, o PIB acima da história.
    """

    spending: float
    phillips: float
    fiscal_risk: float
    gdp: float
    real_rate: float = 0.0
    selic: float = 0.0

    @property
    def total(self) -> float:
        return (
            self.spending
            + self.phillips
            + self.fiscal_risk
            + self.gdp
            + self.real_rate
            + self.selic
        )


class Pressure(Protocol):
    """Os pontos de IPCA que as medidas de gasto somam, desde o primeiro dia em que algum vale."""

    def first_day(self) -> date | None: ...

    def inflation_points(self, day: date) -> float: ...


class Links(Protocol):
    """As ligações do último mês fechado antes de cada dia, desde o primeiro dia em que alguma vale."""

    def first_day(self) -> date | None: ...

    def links_on(self, day: date) -> LinkMonth: ...


class NoLinks:
    def first_day(self) -> date | None:
        return None

    def links_on(self, day: date) -> LinkMonth:
        return NO_LINK


class EconomyLayer:
    """O efeito do governo sobre as séries e os preços da partida; sem efeito nada muda."""

    def __init__(
        self,
        simulation_id: int,
        start: date,
        spending: Pressure,
        links: Links | None = None,
        monetary: Monetary | None = None,
    ):
        self._simulation_id = simulation_id
        self._start = start
        self._spending = spending
        self._links: Links = links or NoLinks()
        self._monetary: Monetary = monetary or AutonomousBank()
        # Memória por dia. Quem lê sem a trava vê o dict antigo ou o novo: o refresh troca o
        # dict inteiro e cada dia entra numa escrita só, que é atômica
        self._spending_points: dict[date, float] = {}
        self._selic_points: dict[date, float] = {}
        self._levels: dict[date, float] = {}
        self._values: dict[IndicatorSeries, dict[date, Decimal]] = {}
        self._betas: dict[str, float] | None = None

    def refresh(self) -> None:
        """As medidas de gasto mudaram: as séries lidas de novo refazem todos os dias."""
        self._spending_points = {}
        self._selic_points = {}
        self._levels = {}
        self._values = {}
        repository.economic.refresh_adjusted(self._simulation_id)

    def refresh_from(self, day: date) -> None:
        """
        As ligações mudaram a partir de `day`: as séries lidas de novo refazem só os dias
        dali em diante. Cada dia depende só dele e dos anteriores, então os de antes valem.
        """
        self._selic_points = {
            d: v for d, v in self._selic_points.copy().items() if d < day
        }
        self._levels = {d: v for d, v in self._levels.copy().items() if d < day}
        self._values = {
            series: {d: v for d, v in values.copy().items() if d < day}
            for series, values in self._values.copy().items()
        }
        repository.economic.refresh_adjusted(self._simulation_id)

    def first_day(self) -> date | None:
        days = [
            d
            for d in (
                self._spending.first_day(),
                self._links.first_day(),
                self._monetary.first_day(),
            )
            if d is not None
        ]
        return min(days, default=None)

    def spending_points(self, day: date) -> float:
        """Pontos de IPCA em 12 meses que as medidas de gasto somam no dia."""
        spending = self._spending_points.get(day)
        if spending is None:
            spending = self._spending.inflation_points(day)
            self._spending_points[day] = spending
        return spending

    def inflation_points(self, day: date) -> float:
        """Pontos de IPCA em 12 meses que o governo soma no dia: as medidas e as ligações."""
        return self.spending_points(day) + self._links.links_on(day).inflation_points

    def reacts(self, day: date) -> bool:
        """A SELIC do dia é a do Banco Central autônomo: nenhuma reunião do governo vale ainda."""
        return self._monetary.selic_on(day) is None

    def selic_points(self, day: date) -> float:
        """Pontos de SELIC acima da série guardada no dia."""
        selic = self._selic_points.get(day)
        if selic is None:
            decided = self._monetary.selic_on(day)
            if decided is None:
                selic = central_bank_reaction(self.inflation_points(day))
            else:
                stored = annual_index_rate(IndicatorSeries.SELIC, day, stored=True)
                selic = float(decided - stored) * 100
            self._selic_points[day] = selic
        return selic

    def level(self, day: date) -> float:
        """O nível da bolsa contra a série guardada."""
        if self.first_day() is None:
            return 1.0
        if day not in self._levels:
            self._levels[day] = math.exp(self.stocks_parts(day).total)
        return self._levels[day]

    def stocks_parts(self, day: date) -> StocksParts:
        """
        O expoente do nível da bolsa por causa. A SELIC e o prêmio pesam pela média do
        trimestre e o PIB pelo desvio do último mês fechado. Cada dia do trimestre conta
        a SELIC de quem a decidia naquele dia.
        """
        links = self._links.links_on

        def reaction(points: Callable[[date], float]) -> Callable[[date], float]:
            return lambda d: central_bank_reaction(points(d)) if self.reacts(d) else 0.0

        def fiscal_risk(d: date) -> float:
            link = links(d)
            inflation = (
                central_bank_reaction(link.premium_inflation_points)
                if self.reacts(d)
                else 0.0
            )
            return inflation + link.premium_points

        def mean(points: Callable[[date], float]) -> float:
            return -STOCKS_PER_SELIC * quarter_mean(points, day)

        return StocksParts(
            spending=mean(reaction(self.spending_points)),
            phillips=mean(reaction(lambda d: links(d).phillips_points)),
            fiscal_risk=mean(fiscal_risk),
            gdp=STOCKS_PER_GDP * float(links(day).gdp_gap),
            real_rate=mean(reaction(lambda d: links(d).rate_points)),
            selic=mean(lambda d: 0.0 if self.reacts(d) else self.selic_points(d)),
        )

    # Contrato com o repositório das séries

    def adjust(
        self, series: IndicatorSeries, history: IndicatorHistory
    ) -> IndicatorHistory:
        first = self.first_day()
        if first is None or series.is_macro:
            return history
        known = self._values.get(series, {})
        computed = {
            day: known[day]
            if day in known
            else self._adjusted(series, history.values[day], day)
            for day in history.dates
            if day >= first
        }
        self._values = {**self._values, series: computed}
        return IndicatorHistory(
            dates=history.dates, values={**history.values, **computed}
        )

    def _adjusted(self, series: IndicatorSeries, value: Decimal, day: date) -> Decimal:
        match series:
            case IndicatorSeries.IPCA:
                # A série é mensal em %: os pontos em 12 meses se dividem pelos meses
                return value + Decimal(str(round(self.inflation_points(day) / 12, 6)))
            case IndicatorSeries.SELIC | IndicatorSeries.CDI:
                annual = float(annualize_daily(value)) + self.selic_points(day) / 100
                return Decimal(str(round(annual_to_daily(annual), 6)))
            case IndicatorSeries.IBOV:
                return Decimal(str(round(float(value) * self.level(day), 2)))
            case IndicatorSeries.GDP_GROWTH | IndicatorSeries.UNEMPLOYMENT:
                return value

    def stock_factor(self, ticker: str, day: date) -> float:
        level = self.level(day)
        return 1.0 if level == 1.0 else level ** self._beta(ticker)

    def _beta(self, ticker: str) -> float:
        if self._betas is None:
            self._betas = self._measure_betas()
        return self._betas.get(ticker, 1.0)

    def _measure_betas(self) -> dict[str, float]:
        """Beta de cada ação contra o Ibovespa nos dois anos anteriores à partida, nas séries guardadas."""
        end = self._start - timedelta(days=1)
        begin = end - timedelta(days=BETA_WINDOW_DAYS)
        reference = repository.economic.get_history(
            IndicatorSeries.IBOV, self._simulation_id, stored=True
        )
        market = _returns(
            {
                d: float(reference.values[d])
                for d in reference.dates
                if begin <= d <= end
            }
        )
        tickers = [stock.ticker for stock in repository.stock.get_stocks()]
        closes = repository.stock.get_closes_between(
            tickers, begin, end, self._simulation_id
        )
        return {ticker: beta_of(_returns(closes[ticker]), market) for ticker in tickers}


def _returns(levels: dict[date, float]) -> dict[date, float]:
    """Retorno de cada pregão contra o anterior."""
    days = sorted(levels)
    return {
        day: levels[day] / levels[previous] - 1
        for previous, day in pairwise(days)
        if levels[previous]
    }


def beta_of(asset: dict[date, float], market: dict[date, float]) -> float:
    """Quanto o ativo anda por ponto que o mercado anda: covariância ÷ variância do mercado nos dias em comum; 1 quando faltam dias."""
    common = [d for d in asset if d in market]
    if len(common) < MIN_BETA_DAYS:
        return 1.0
    xs = [market[d] for d in common]
    ys = [asset[d] for d in common]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    variance = sum((x - mean_x) ** 2 for x in xs)
    if variance == 0:
        return 1.0
    covariance = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    return max(0.0, min(MAX_BETA, covariance / variance))
