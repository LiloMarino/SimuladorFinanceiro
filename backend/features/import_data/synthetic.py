"""
Gerador de séries sintéticas: um futuro plausível para depois do último dia real.

Bootstrap em blocos conjunto: o futuro é montado com trechos reais de 60 pregões
do histórico, e o mesmo trecho vale para todos os ativos e indicadores no mesmo
dia. Crises, volatilidade que dura e setores andando juntos vêm do próprio
histórico. Os trechos se encadeiam por bioma (calmo, normal, agitado) com as
transições medidas no histórico, e a temperatura pesa o sorteio pela
volatilidade de cada trecho: em 1 o histórico como foi, abaixo favorece os
calmos, acima os agitados.

Encaixe de nível: entre os trechos do bioma, o sorteio favorece os que começam
com SELIC, inflação de 12 meses e tendência da inflação parecidas com as do
momento gerado. É o que mantém o juro real plausível e a SELIC reagindo à
inflação como no histórico.

Inflação por regime: duas camadas por cima do sorteio, que mudam os níveis sem
mudar os trechos.
- O nível sobe em seis meses e fica. Soma X pontos à inflação anual; a SELIC
  reage 1,5·X na subida (princípio de Taylor: o juro sobe mais que a inflação) e
  assenta em +X, de modo que o juro real volta ao de antes. A bolsa reage ao
  juro real pela reação histórica do Ibovespa à SELIC, cada ativo pelo seu beta:
  cai enquanto a SELIC está acima da inflação somada e recupera quando ela
  assenta. Por cima, todo ativo sobe com a inflação somada no nominal.
- Os surtos são pulsos que sobem em seis meses e decaem pela metade a cada ano,
  sorteados ano a ano pela semente. Cada um soma pontos à inflação anual, 1,5x
  isso à SELIC e a reação da bolsa à SELIC, sem repasse nominal.

Dividendos: o caminho sorteado é de retorno total (o preço mais o provento). O
ativo que pagava continua pagando: o rendimento anual e os meses de pagamento vêm
dos últimos anos reais, e cada data ex gerada tira do preço o valor pago, como no
mercado. O gerador não sorteia desdobramento.

É uma conta pura sobre o histórico recebido: nada aqui lê ou grava no banco.
"""

import logging
import zlib
from bisect import bisect_left
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import IntEnum

import numpy as np
import pandas as pd

from backend.core.enum import CorporateEventKind, IndicatorSeries
from backend.core.periods import BUSINESS_DAYS_PER_YEAR, MONTHS_PER_YEAR
from backend.core.utils import (
    business_days_between,
    next_business_day,
    subtract_months,
)

logger = logging.getLogger(__name__)

BLOCK_DAYS = 60
MIN_TEMPERATURE, MAX_TEMPERATURE = 0.0, 3.0
# Expoente da temperatura: em T = 2 a volatilidade fica no nível do pior ano real
TEMPERATURE_STEEPNESS = 2.0

# O sorteio começa no regime de metas de inflação; antes dele a SELIC tem
# valores de hiperinflação. A data também é a âncora da grade de blocos.
POOL_START = date(2000, 1, 3)

# Variação diária fora desta faixa é erro de dado da fonte (preço que vai a ~0 e
# volta), e o dia conta como sem retorno do ativo
MAX_DAILY_UP, MAX_DAILY_DOWN = np.log(2.0), np.log(0.5)

# Pregões em comum para estimar o beta de um ativo contra a referência
MIN_FIT_DAYS = 60

# Largura do encaixe de nível, em desvios-padrão do estado dos trechos
MATCH_BANDWIDTH = 0.5
# Nível da inflação, em pontos percentuais da inflação anual
MIN_INFLATION_LEVEL, MAX_INFLATION_LEVEL = -5.0, 20.0
# Surtos de inflação: quantos por década e a intensidade média, em pontos
MIN_SURGE_FREQUENCY, MAX_SURGE_FREQUENCY = 0.0, 5.0
MIN_SURGE_INTENSITY, MAX_SURGE_INTENSITY = 2.0, 20.0
SURGES_DECADE_YEARS = 10
SURGE_SALT = zlib.crc32(b"inflation-surge")
SHOCK_RAMP_YEARS, SHOCK_HALF_LIFE_YEARS = 0.5, 1.0
# O calendário gerado tem um pregão por dia útil da semana, sem feriado: é a régua do
# tempo do nível e dos surtos, para que um ano deles seja um ano do IPCA mensal
WEEKDAYS_PER_YEAR = 365.25 * 5 / 7
SELIC_SHOCK_RESPONSE = 1.5
SELIC_FLOOR = 0.005
QUARTER_DAYS = 63
# O juro americano do futuro volta ao patamar de longo prazo do Fed (3% ao ano), perdendo
# metade da distância a cada 2 anos; é um caminho único, sem sorteio
FED_LONG_RUN = 3.0
FED_HALF_LIFE_YEARS = 2.0

PRICE_COLUMNS = ["open", "high", "low", "close", "volume"]

# Anos reais (de 12 meses completos) que calibram o rendimento do dividendo
DIVIDEND_YEARS = 5
# Anos sem dividendo, os mais recentes, a partir dos quais o ativo deixa de pagar
SILENT_YEARS = 2
# O rendimento de cada ano gerado varia em torno da média por até esta fração
DIVIDEND_VARIATION = 0.3
DIVIDEND_SALT = zlib.crc32(b"dividend")
# Um pagamento nunca tira mais que esta fração do preço
MAX_PAYMENT_SHARE = 0.5
# Sem histórico para calibrar, o ativo paga a média do segmento nestes meses, no dia 15
NEW_ASSET_PAY_MONTHS = (3, 6, 9, 12)
NEW_ASSET_PAY_DAY = 15
# Dia máximo do mês da data ex típica: todo mês tem
MAX_PAY_DAY = 28


class Regime(IntEnum):
    """Bioma de um trecho, pelo tercil da volatilidade do Ibovespa nele."""

    CALM = 0
    NORMAL = 1
    AGITATED = 2


@dataclass(frozen=True)
class AssetHistory:
    """Pregões reais de um ativo: índice de datas e as colunas de `PRICE_COLUMNS`."""

    bars: pd.DataFrame
    segment: str | None = None
    sector: str | None = None
    # Razão do desdobramento (2 é 2:1) e dividendo bruto por cota, por data ex; os
    # preços de `bars` são os negociados na época
    splits: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    dividends: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    # Cripto não paga dividendo
    pays_dividends: bool = True


@dataclass(frozen=True)
class MarketHistory:
    """
    Toda a base real. Indicadores como o Banco Central publica: CDI e SELIC em %
    ao dia útil, IPCA em % ao mês datado no dia 1, IBOV em pontos.
    """

    assets: dict[str, AssetHistory]
    indicators: dict[IndicatorSeries, pd.Series]


@dataclass(frozen=True)
class GeneratedEvent:
    """Provento gerado: dividendo bruto por cota na data ex."""

    ex_date: date
    kind: CorporateEventKind
    value: float


@dataclass(frozen=True)
class GeneratedSeries:
    """Linhas geradas, no mesmo formato da entrada, prontas para gravar como geradas."""

    assets: dict[str, pd.DataFrame] = field(default_factory=dict)
    indicators: dict[IndicatorSeries, pd.Series] = field(default_factory=dict)
    events: dict[str, list[GeneratedEvent]] = field(default_factory=dict)


@dataclass(frozen=True)
class _DividendProfile:
    """O que o histórico diz do pagamento: anos completos, rendimento médio e calendário."""

    years: int
    average_yield: float
    # Mês do pagamento e o dia típico dele
    calendar: dict[int, int]
    silent: bool


def _clean(returns: np.ndarray) -> np.ndarray:
    out = returns.copy()
    out[(out > MAX_DAILY_UP) | (out < MAX_DAILY_DOWN)] = np.nan
    return out


def _warn_missing_prices(ticker: str, level: pd.Series) -> None:
    """Avisa no log os pregões reais sem preço, que o gerador lê como dia sem negócio."""
    zeros = _dates(level.index[level.to_numpy() <= 0])
    if len(zeros):
        logger.warning(
            "'%s' tem fechamento zerado em %s pregões reais (de %s a %s): o gerador "
            "os trata como dias sem negócio. Corrija com 'Corrigir erros' ou "
            "reimportando o ativo.",
            ticker,
            len(zeros),
            zeros[0],
            zeros[-1],
        )


def to_annual(daily_pct: np.ndarray) -> np.ndarray:
    return (1 + daily_pct / 100) ** BUSINESS_DAYS_PER_YEAR - 1


def to_daily(annual: np.ndarray) -> np.ndarray:
    return ((1 + annual) ** (1 / BUSINESS_DAYS_PER_YEAR) - 1) * 100


def _day_number(day: date) -> int:
    return business_days_between(POOL_START, day)


def _block_of(day: date) -> tuple[int, int]:
    """Bloco da grade fixa a que o dia útil pertence e a posição dele no bloco."""
    return divmod(_day_number(day), BLOCK_DAYS)


def _day_from_number(number: int) -> date:
    """Inverso de `_day_number`: POOL_START é uma segunda-feira."""
    weeks, rest = divmod(number, 5)
    return POOL_START + timedelta(days=weeks * 7 + rest)


def _first_business_day(month: date) -> date:
    return month if month.weekday() < 5 else next_business_day(month)


def _accumulated(monthly_pct: list[float]) -> float:
    return float(np.prod(1 + np.array(monthly_pct) / 100) - 1)


def _by_datetime[T: (pd.Series, pd.DataFrame)](data: T) -> T:
    out = data.astype(float)
    out.index = pd.to_datetime(out.index)
    return out.sort_index()


def _dates(index: pd.Index) -> list[date]:
    return index.to_numpy().astype("datetime64[D]").tolist()


def _last_day(data: pd.Series | pd.DataFrame) -> date:
    return _dates(data.index)[-1]


def _business_days(after: date, until: date) -> list[date]:
    days: list[date] = []
    day = next_business_day(after)
    while day <= until:
        days.append(day)
        day = next_business_day(day)
    return days


class SeriesGenerator:
    """
    Pré-calcula o histórico uma vez (calendário, trechos, biomas, estado
    econômico, retornos) para que gerações seguidas, como as de um preview, saiam
    baratas.
    """

    def __init__(self, history: MarketHistory):
        self.history = history
        self.indicators = {
            series: _by_datetime(values)
            for series, values in history.indicators.items()
            if not values.empty
        }
        if IndicatorSeries.IBOV not in self.indicators:
            raise ValueError("O Ibovespa é a referência do sorteio e precisa existir.")

        # Calendário do sorteio: os pregões do Ibovespa desde POOL_START
        ibov = self.indicators[IndicatorSeries.IBOV]
        ibov = ibov.loc[ibov.index >= pd.Timestamp(POOL_START)]
        self.calendar = pd.DatetimeIndex(ibov.index)
        self.calendar_days = _dates(self.calendar)
        levels = ibov.to_numpy()
        self.market = np.concatenate([[np.nan], np.log(levels[1:] / levels[:-1])])

        # Trechos candidatos e o bioma de cada um
        self.starts = np.arange(1, len(self.calendar) - BLOCK_DAYS + 1)
        rolling = pd.Series(self.market).rolling(BLOCK_DAYS).std()
        self.block_vol = rolling.shift(-(BLOCK_DAYS - 1)).to_numpy()[self.starts]
        cuts = np.quantile(self.block_vol, [1 / 3, 2 / 3])
        self.regime = np.digitize(self.block_vol, cuts)
        self.members = [np.flatnonzero(self.regime == r) for r in Regime]

        # Transições entre biomas de um trecho para o seguinte, como no histórico
        counts = np.zeros((len(Regime), len(Regime)))
        following = self.regime[BLOCK_DAYS:]
        np.add.at(counts, (self.regime[: len(following)], following), 1)
        self.transitions = counts / counts.sum(axis=1, keepdims=True)

        # A cadeia nasce no bloco do último pregão real, no bioma do mercado de hoje
        self.current_regime = Regime(
            int(np.digitize(np.nanstd(self.market[-BLOCK_DAYS:]), cuts))
        )
        self.anchor_block = _block_of(self.calendar_days[-1])[0]
        # O nível e os surtos começam no primeiro dia depois do último pregão real
        self.shock_start = _day_number(self.calendar_days[-1]) + 1
        self._prepare_economy()

        self._paths: dict[tuple[int, float], _Path] = {}
        self._bars: dict[str, pd.DataFrame] = {}
        self._returns: dict[str, np.ndarray] = {}
        self._profiles: dict[str, _DividendProfile] = {}
        self._group_means: dict[tuple[str, str], np.ndarray] = {}

    def _prepare_economy(self) -> None:
        """SELIC anual e IPCA de 12 meses em cada pregão, e o estado de cada trecho."""
        n = len(self.calendar)
        selic = self.indicators.get(IndicatorSeries.SELIC)
        ipca = self.indicators.get(IndicatorSeries.IPCA)
        self.selic_end = _last_day(selic) if selic is not None else None
        self.ipca_end = _last_day(ipca) if ipca is not None else None

        self.selic_annual = np.full(n, np.nan)
        self.last_selic = np.nan
        if selic is not None:
            self.selic_annual = to_annual(
                selic.reindex(self.calendar, method="ffill").to_numpy()
            )
            self.last_selic = float(to_annual(np.array([selic.iloc[-1]]))[0])
        self.selic_changes = np.nan_to_num(np.diff(self.selic_annual, prepend=np.nan))
        with np.errstate(all="ignore"):
            self.selic_floor = np.nanmin(self.selic_annual, initial=np.inf)
            self.selic_ceiling = np.nanmax(self.selic_annual, initial=-np.inf)

        self.ipca_by_month: dict[date, float] = {}
        self.last_ipca: list[float] = []
        ipca12 = np.full(n, np.nan)
        trend = np.full(n, np.nan)
        if ipca is not None:
            months = _dates(ipca.index)
            self.ipca_by_month = dict(zip(months, ipca.to_numpy(), strict=True))
            self.last_ipca = list(ipca.to_numpy()[-12:])
            rolling = (ipca / 100 + 1).rolling(12).apply(np.prod) - 1
            accumulated = dict(zip(months, rolling.to_numpy(), strict=True))
            for i, day in enumerate(self.calendar_days):
                month = day.replace(day=1)
                before = subtract_months(month, 3)
                ipca12[i] = accumulated.get(month, np.nan)
                trend[i] = ipca12[i] - accumulated.get(before, np.nan)

        # Estado no início de cada trecho, em desvios-padrão, para o encaixe
        state = np.vstack([self.selic_annual, ipca12, trend])[:, self.starts]
        with np.errstate(all="ignore"):
            scale = np.nanstd(state, axis=1, keepdims=True)
        self.state_scale = np.where(scale > 0, scale, 1.0)
        self.trecho_state = state / self.state_scale

        # Reação histórica do Ibovespa à SELIC: retorno do trimestre por ponto de
        # variação da SELIC no mesmo trimestre
        self.market_selic_beta = 0.0
        if selic is not None:
            edges = np.arange(1, n - QUARTER_DAYS, QUARTER_DAYS)
            moves = np.array(
                [np.nansum(self.market[e : e + QUARTER_DAYS]) for e in edges]
            )
            ends = self.selic_annual[edges + QUARTER_DAYS - 1]
            changes = ends - self.selic_annual[edges - 1]
            if np.var(changes) > 0:
                self.market_selic_beta = float(
                    np.cov(changes, moves)[0, 1] / np.var(changes, ddof=1)
                )

    def generate(
        self,
        until: date,
        seed: int,
        temperature: float = 1.0,
        inflation_level: float = 0.0,
        surge_frequency: float = 0.0,
        surge_intensity: float = 6.0,
        tickers: Iterable[str] | None = None,
    ) -> GeneratedSeries:
        """
        Cada série recebe os dias úteis desde o dia seguinte ao seu último dado
        real até `until`. O trecho sorteado para cada data depende só da semente,
        da temperatura e da data: gerar um ativo sozinho dá as mesmas linhas que
        gerá-lo junto com os outros. O nível da inflação (pontos percentuais) e os
        surtos (quantos por década e a intensidade em pontos) mudam os níveis sem
        mudar os trechos.
        """
        if not MIN_TEMPERATURE <= temperature <= MAX_TEMPERATURE:
            raise ValueError(
                f"Temperatura fora de [{MIN_TEMPERATURE}, {MAX_TEMPERATURE}]."
            )
        if not MIN_INFLATION_LEVEL <= inflation_level <= MAX_INFLATION_LEVEL:
            raise ValueError(
                "Nível da inflação fora de "
                f"[{MIN_INFLATION_LEVEL}, {MAX_INFLATION_LEVEL}] pontos."
            )
        if not MIN_SURGE_FREQUENCY <= surge_frequency <= MAX_SURGE_FREQUENCY:
            raise ValueError(
                "Frequência dos surtos fora de "
                f"[{MIN_SURGE_FREQUENCY}, {MAX_SURGE_FREQUENCY}] por década."
            )
        if not MIN_SURGE_INTENSITY <= surge_intensity <= MAX_SURGE_INTENSITY:
            raise ValueError(
                "Intensidade dos surtos fora de "
                f"[{MIN_SURGE_INTENSITY}, {MAX_SURGE_INTENSITY}] pontos."
            )
        draw = _Draw(
            seed,
            temperature,
            inflation_level / 100,
            surge_frequency / SURGES_DECADE_YEARS,
            surge_intensity / 100,
        )
        selected = self.history.assets if tickers is None else tickers
        result = GeneratedSeries()
        for ticker in selected:
            generated = self._generate_asset(draw, ticker, until)
            if generated is not None:
                result.assets[ticker], result.events[ticker] = generated
        self._generate_indicators(draw, until, result.indicators)
        return result

    # ------------------------------------------------------------------
    # Sorteio dos trechos e caminho da economia

    def _path(self, draw: "_Draw", last_day: date) -> "_Path":
        """
        Percorre os dias desde o bloco âncora sorteando um trecho por bloco e
        levando junto a SELIC e o IPCA sem nível nem surtos: o encaixe do próximo
        trecho depende do estado a que os anteriores levaram.
        """
        key = (draw.seed, draw.temperature)
        cached = self._paths.get(key)
        if cached is not None and cached.last_day >= last_day:
            return cached

        relative = self.block_vol / np.median(self.block_vol)
        heat = relative ** (TEMPERATURE_STEEPNESS * (draw.temperature - 1))
        path = _Path(last_day)
        level = self.last_selic
        recent_ipca = list(self.last_ipca)
        ipca12 = [_accumulated(recent_ipca)] * 4 if recent_ipca else [np.nan] * 4
        regime = self.current_regime

        number = self.anchor_block * BLOCK_DAYS
        day = _day_from_number(number)
        while day <= last_day:
            block, offset = divmod(number, BLOCK_DAYS)
            if block not in path.chain:
                current = np.array([level, ipca12[-1], ipca12[-1] - ipca12[-4]])
                distance = np.nansum(
                    (self.trecho_state - current[:, None] / self.state_scale) ** 2,
                    axis=0,
                )
                fit = np.exp(-0.5 * (distance - distance.min()) / MATCH_BANDWIDTH**2)
                weights = heat * fit
                u_regime, u_block = np.random.default_rng([draw.seed, block]).random(2)
                if block > self.anchor_block:
                    # A temperatura e o encaixe também inclinam a troca de bioma
                    tilted = self.transitions[regime] * np.array(
                        [weights[m].mean() for m in self.members]
                    )
                    cdf = np.cumsum(tilted / tilted.sum())
                    regime = Regime(int(min(np.searchsorted(cdf, u_regime), 2)))
                members = self.members[regime]
                cdf = np.cumsum(weights[members] / weights[members].sum())
                i = min(np.searchsorted(cdf, u_block), len(members) - 1)
                path.chain[block] = int(self.starts[members[i]])
            source = path.chain[block] + offset

            # IPCA do mês: o do mês sorteado para o primeiro dia útil dele
            month = day.replace(day=1)
            if (
                self.ipca_end is not None
                and month > self.ipca_end
                and day == _first_business_day(month)
            ):
                value = self.ipca_by_month.get(
                    self.calendar_days[source].replace(day=1), recent_ipca[-1]
                )
                path.ipca[month] = value
                recent_ipca = [*recent_ipca[-11:], value]
                ipca12.append(_accumulated(recent_ipca))

            # SELIC: nível de hoje mais as variações dos trechos, nos limites
            if self.selic_end is not None and day > self.selic_end:
                level = min(
                    max(level + self.selic_changes[source], self.selic_floor),
                    self.selic_ceiling,
                )
                path.selic[day] = level

            number += 1
            day = _day_from_number(number)
        self._paths[key] = path
        return path

    def _sources(self, draw: "_Draw", days: list[date]) -> np.ndarray:
        """Posição no calendário do sorteio do pregão real que cada dia copia."""
        chain = self._path(draw, days[-1]).chain
        return np.array(
            [
                chain[max(block, self.anchor_block)] + offset
                for block, offset in map(_block_of, days)
            ]
        )

    def _surges(self, draw: "_Draw", last_year: int) -> list[tuple[float, float]]:
        """
        Surtos do sorteio como (início em anos desde `shock_start`, amplitude em
        fração). Cada ano `k` tem o próprio sorteio: aumentar a frequência só
        acrescenta surtos e eles dependem só da semente e do ano.
        """
        surges = []
        for k in range(last_year + 1):
            u1, u2, u3 = np.random.default_rng([draw.seed, SURGE_SALT, k]).random(3)
            if u1 < draw.surge_frequency:
                surges.append((k + float(u2), draw.surge_intensity * (0.5 + float(u3))))
        return surges

    def _effects(
        self, draw: "_Draw", numbers: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        O que o nível e os surtos somam em cada pregão (número de dia útil), em
        fração ao ano: a inflação e a SELIC, antes do piso da SELIC. O nível sobe em
        seis meses e fica; a SELIC reage 1,5x na subida e assenta em 1x. Cada surto
        é um pulso que sobe em seis meses e decai pela metade a cada ano, com a SELIC
        a 1,5x.
        """
        elapsed = (numbers - self.shock_start) / WEEKDAYS_PER_YEAR
        years = np.maximum(elapsed, 0.0)
        level = draw.level * _ramp(years)
        inflation = level.copy()
        selic = level * (1 + (SELIC_SHOCK_RESPONSE - 1) * _decay(years))
        for start, amplitude in self._surges(draw, int(years.max(initial=0.0))):
            since = np.maximum(elapsed - start, 0.0)
            pulse = amplitude * _ramp(since) * _decay(since)
            inflation += pulse
            selic += SELIC_SHOCK_RESPONSE * pulse
        return inflation, selic

    def _shock_moves(self, draw: "_Draw", days: list[date]) -> np.ndarray:
        """
        Retorno extra do Ibovespa em cada dia pelo juro que o nível e os surtos
        empurraram. Do nível conta só o que a SELIC sobe além da inflação dele (o juro
        real), que se desfaz quando a SELIC assenta; dos surtos conta a SELIC inteira.
        """
        if not draw.level and not draw.surge_frequency:
            return np.zeros(len(days))
        # O dia útil anterior ao primeiro é o ponto de partida da diferença
        numbers = np.array([_day_number(d) for d in days])
        numbers = np.concatenate([[numbers[0] - 1], numbers])
        _, selic_push = self._effects(draw, numbers)
        years = np.maximum(numbers - self.shock_start, 0) / WEEKDAYS_PER_YEAR
        rate_push = selic_push - draw.level * _ramp(years)
        return self.market_selic_beta * np.diff(rate_push)

    def _passthrough(self, draw: "_Draw", days: list[date]) -> np.ndarray:
        """Retorno extra de cada dia pelo repasse nominal da inflação do nível, igual em todo ativo."""
        numbers = np.array([_day_number(d) for d in days])
        years = np.maximum(numbers - self.shock_start, 0) / WEEKDAYS_PER_YEAR
        return np.log1p(draw.level * _ramp(years)) / WEEKDAYS_PER_YEAR

    # ------------------------------------------------------------------
    # Ativos

    def _asset_bars(self, ticker: str) -> pd.DataFrame:
        if ticker not in self._bars:
            self._bars[ticker] = _by_datetime(self.history.assets[ticker].bars)
        return self._bars[ticker]

    def _total_return_level(self, ticker: str) -> pd.Series:
        """
        O fechamento com os eventos embutidos: o desdobramento não derruba o nível e
        o dividendo entra como se fosse reinvestido na data ex. O retorno dele é o
        que o ativo deu a quem o segurou.
        """
        bars = self._asset_bars(ticker)
        asset = self.history.assets[ticker]
        close = bars["close"]
        ratio = _by_datetime(asset.splits).reindex(bars.index).fillna(1.0)
        dividend = _by_datetime(asset.dividends).reindex(bars.index).fillna(0.0)
        with np.errstate(all="ignore"):
            step = np.where(close > 0, ratio * (close + dividend) / close, 1.0)
        return pd.Series(close.to_numpy() * np.cumprod(step), index=bars.index)

    def _asset_returns(self, ticker: str) -> np.ndarray:
        if ticker not in self._returns:
            close = self._total_return_level(ticker)
            _warn_missing_prices(ticker, close)
            # Fechamento zerado é pregão sem preço: entra como dia sem negócio
            levels = close.reindex(self.calendar).to_numpy()
            levels = np.where(levels > 0, levels, np.nan)
            returns = np.concatenate([[np.nan], np.log(levels[1:] / levels[:-1])])
            self._returns[ticker] = _clean(returns)
        return self._returns[ticker]

    def _group_mean(self, ticker: str, group: str) -> np.ndarray | None:
        """Retorno médio dos outros ativos do mesmo segmento ou setor, dia a dia."""
        key = getattr(self.history.assets[ticker], group)
        if key is None:
            return None
        peers = [
            t
            for t, asset in self.history.assets.items()
            if t != ticker and getattr(asset, group) == key
        ]
        if not peers:
            return None
        cache_key = (ticker, group)
        if cache_key not in self._group_means:
            stack = np.vstack([self._asset_returns(t) for t in peers])
            with np.errstate(all="ignore"):
                counts = (~np.isnan(stack)).sum(axis=0)
                sums = np.nansum(stack, axis=0)
                self._group_means[cache_key] = np.where(
                    counts > 0, sums / counts, np.nan
                )
        return self._group_means[cache_key]

    def _generate_asset(
        self, draw: "_Draw", ticker: str, until: date
    ) -> tuple[pd.DataFrame, list[GeneratedEvent]] | None:
        bars = self._asset_bars(ticker)
        returns = self._asset_returns(ticker)
        own = ~np.isnan(returns)
        own_days = np.flatnonzero(own)
        days = _business_days(_last_day(bars), until)
        if not days or not len(own_days):
            return None
        sources = self._sources(draw, days)

        # Proporções do pregão real: abertura sobre o fechamento anterior, máxima
        # e mínima sobre o fechamento, volume sobre o volume mediano do ano
        aligned = bars.reindex(self.calendar)
        median_volume = bars["volume"].rolling(BUSINESS_DAYS_PER_YEAR, min_periods=20)
        median_volume = median_volume.median().reindex(self.calendar)
        open_ratio = (aligned["open"] / aligned["close"].shift(1)).clip(0.5, 2.0)
        high_ratio = (aligned["high"] / aligned["close"]).clip(1.0, 2.0)
        low_ratio = (aligned["low"] / aligned["close"]).clip(0.5, 1.0)
        volume_ratio = aligned["volume"] / median_volume.where(median_volume > 0)

        # Dia sorteado em que o ativo não negociou: o movimento dos pares do
        # segmento, do setor ou do Ibovespa, nessa ordem, com o beta e um resíduo
        # sorteado do próprio ativo
        references = [
            ref
            for ref in (
                self._group_mean(ticker, "segment"),
                self._group_mean(ticker, "sector"),
            )
            if ref is not None
        ]
        references.append(self.market)
        fits: list[tuple[np.ndarray, float, np.ndarray]] = []
        for ref in references:
            common = own & ~np.isnan(ref)
            if common.sum() < MIN_FIT_DAYS:
                continue
            x, y = ref[common], returns[common]
            beta = float(np.cov(x, y)[0, 1] / np.var(x, ddof=1))
            fits.append((ref, beta, y - beta * x))

        salt = zlib.crc32(ticker.encode())
        generated = np.empty(len(days))
        ratio_day = np.empty(len(days), dtype=int)
        for j, (day, source) in enumerate(zip(days, sources, strict=True)):
            if own[source] and not np.isnan(open_ratio.iloc[source]):
                generated[j], ratio_day[j] = returns[source], source
                continue
            rng = np.random.default_rng([draw.seed, _day_number(day), salt])
            ratio_day[j] = int(own_days[rng.integers(len(own_days))])
            fit = next((f for f in fits if not np.isnan(f[0][source])), None)
            if fit is None:
                generated[j] = returns[ratio_day[j]]
            else:
                ref, beta, residuals = fit
                generated[j] = (
                    beta * ref[source] + residuals[rng.integers(len(residuals))]
                )

        # A reação à SELIC chega ao ativo pelo beta dele contra o Ibovespa; o repasse
        # da inflação, inteiro
        market_beta = next((b for ref, b, _ in fits if ref is self.market), 1.0)
        generated += market_beta * self._shock_moves(draw, days)
        generated += self._passthrough(draw, days)

        last_close = float(bars["close"].iloc[-1])
        close = last_close * np.exp(np.cumsum(generated))
        previous = np.concatenate([[last_close], close[:-1]])
        open_ = previous * open_ratio.fillna(1.0).to_numpy()[ratio_day]
        high = np.maximum.reduce(
            [close * high_ratio.fillna(1.0).to_numpy()[ratio_day], open_, close]
        )
        low = np.minimum.reduce(
            [close * low_ratio.fillna(1.0).to_numpy()[ratio_day], open_, close]
        )
        recent_volume = float(bars["volume"].iloc[-BUSINESS_DAYS_PER_YEAR:].median())
        volume = np.round(
            volume_ratio.fillna(1.0).to_numpy()[ratio_day] * recent_volume
        ).astype(np.int64)

        # O caminho acima é de retorno total: cada data ex tira do preço, daquele dia
        # em diante, o dividendo pago
        events, markdown = self._dividends(draw, ticker, days, close, last_close)
        frame = pd.DataFrame(
            {
                "open": open_ * markdown,
                "high": high * markdown,
                "low": low * markdown,
                "close": close * markdown,
                "volume": volume,
            },
            index=pd.Index(days, name="date"),
        )
        return frame, events

    # ------------------------------------------------------------------
    # Dividendos

    def _dividend_profile(self, ticker: str) -> _DividendProfile:
        """
        Os últimos anos reais do ativo, de 12 meses completos contados do último
        pregão (até `DIVIDEND_YEARS`): o rendimento anual de cada um é o que ele
        pagou sobre o preço médio do ano.
        """
        if ticker in self._profiles:
            return self._profiles[ticker]
        bars = self._asset_bars(ticker)
        dividends = pd.Series(_by_datetime(self.history.assets[ticker].dividends))
        last, first = bars.index[-1], bars.index[0]
        yields: list[float] = []
        days_of_month: dict[int, list[int]] = {}
        for k in range(DIVIDEND_YEARS):
            end = last - pd.DateOffset(months=12 * k)
            start = last - pd.DateOffset(months=12 * (k + 1))
            if start < first:
                break
            closes = bars["close"].loc[(bars.index > start) & (bars.index <= end)]
            paid = dividends.loc[(dividends.index > start) & (dividends.index <= end)]
            if closes.empty:
                break
            yields.append(float(paid.sum() / closes.mean()))
            for day in paid.index:
                days_of_month.setdefault(day.month, []).append(day.day)
        profile = _DividendProfile(
            years=len(yields),
            average_yield=float(np.mean(yields)) if yields else 0.0,
            calendar={
                month: int(np.median(days)) for month, days in days_of_month.items()
            },
            silent=len(yields) >= SILENT_YEARS and not any(yields[:SILENT_YEARS]),
        )
        self._profiles[ticker] = profile
        return profile

    def _segment_yield(self, ticker: str) -> float:
        """Rendimento médio dos outros ativos do segmento (senão do setor) com histórico para calibrar."""
        asset = self.history.assets[ticker]
        for group in ("segment", "sector"):
            key = getattr(asset, group)
            if key is None:
                continue
            peers = [
                self._dividend_profile(t)
                for t, other in self.history.assets.items()
                if t != ticker and other.pays_dividends and getattr(other, group) == key
            ]
            yields = [p.average_yield for p in peers if p.years >= SILENT_YEARS]
            if yields:
                return float(np.mean(yields))
        return 0.0

    def _payment_plan(self, ticker: str) -> tuple[float, dict[int, int]]:
        """Rendimento anual e calendário (mês e dia típico) com que o ativo paga; vazio quando não paga."""
        if not self.history.assets[ticker].pays_dividends:
            return 0.0, {}
        profile = self._dividend_profile(ticker)
        if profile.years >= SILENT_YEARS:
            if profile.silent:
                return 0.0, {}
            return profile.average_yield, profile.calendar
        return self._segment_yield(ticker), dict.fromkeys(
            NEW_ASSET_PAY_MONTHS, NEW_ASSET_PAY_DAY
        )

    def _dividends(
        self,
        draw: "_Draw",
        ticker: str,
        days: list[date],
        total_return: np.ndarray,
        last_close: float,
    ) -> tuple[list[GeneratedEvent], np.ndarray]:
        """
        Os dividendos gerados e o fator que cada pregão aplica ao caminho de retorno
        total. O valor de cada pagamento é a fatia do rendimento do ano sobre o
        fechamento da véspera já com as quedas anteriores; a queda da data ex é essa
        mesma fatia do preço.
        """
        markdown = np.ones(len(days))
        annual_yield, calendar = self._payment_plan(ticker)
        if annual_yield <= 0 or not calendar:
            return [], markdown

        salt = zlib.crc32(ticker.encode())
        pay_days: dict[int, float] = {}
        for year in range(days[0].year, days[-1].year + 1):
            rng = np.random.default_rng([draw.seed, year, salt, DIVIDEND_SALT])
            varied = annual_yield * (
                1 + DIVIDEND_VARIATION * (2 * float(rng.random()) - 1)
            )
            share = min(varied / len(calendar), MAX_PAYMENT_SHARE)
            for month, day in calendar.items():
                target = date(year, month, min(day, MAX_PAY_DAY))
                if not days[0] <= target <= days[-1]:
                    continue
                pay_days.setdefault(bisect_left(days, target), share)

        events: list[GeneratedEvent] = []
        level = 1.0
        for index in sorted(pay_days):
            share = pay_days[index]
            before = last_close if index == 0 else float(total_return[index - 1])
            events.append(
                GeneratedEvent(
                    ex_date=days[index],
                    kind=CorporateEventKind.DIVIDEND,
                    value=round(share * before * level, 6),
                )
            )
            level *= 1 - share
            markdown[index:] = level
        return events, markdown

    # ------------------------------------------------------------------
    # Indicadores

    def _generate_indicators(
        self, draw: "_Draw", until: date, out: dict[IndicatorSeries, pd.Series]
    ) -> None:
        # Ibovespa: pontos, como o fechamento de um ativo
        ibov = self.indicators[IndicatorSeries.IBOV]
        days = _business_days(_last_day(ibov), until)
        if days:
            moves = self.market[self._sources(draw, days)]
            moves = (
                moves + self._shock_moves(draw, days) + self._passthrough(draw, days)
            )
            out[IndicatorSeries.IBOV] = pd.Series(
                float(ibov.iloc[-1]) * np.exp(np.cumsum(moves)), index=days
            )

        selic = self.indicators.get(IndicatorSeries.SELIC)
        cdi = self.indicators.get(IndicatorSeries.CDI)
        if selic is not None and cdi is not None:
            self._generate_rates(draw, until, selic, cdi, out)
        if self.ipca_end is not None:
            self._generate_ipca(draw, until, out)
        fed = self.indicators.get(IndicatorSeries.FED_FUNDS)
        if fed is not None:
            self._generate_fed(until, fed, out)

    def _generate_fed(
        self, until: date, fed: pd.Series, out: dict[IndicatorSeries, pd.Series]
    ) -> None:
        """O Fed Funds em % ao ano, do último valor real até o patamar de longo prazo."""
        last_day, last = _last_day(fed), float(fed.iloc[-1])
        days = _business_days(last_day, until)
        if not days:
            return
        years = np.array([(day - last_day).days for day in days]) / 365.25
        values = FED_LONG_RUN + (last - FED_LONG_RUN) * 0.5 ** (
            years / FED_HALF_LIFE_YEARS
        )
        out[IndicatorSeries.FED_FUNDS] = pd.Series(np.round(values, 4), index=days)

    def _generate_rates(
        self,
        draw: "_Draw",
        until: date,
        selic: pd.Series,
        cdi: pd.Series,
        out: dict[IndicatorSeries, pd.Series],
    ) -> None:
        """
        A SELIC do caminho mais o empurrão do nível e dos surtos; o CDI anda colado
        nela, com o spread do último dia real.
        """
        cdi_end = _last_day(cdi)
        days = _business_days(min(_last_day(selic), cdi_end), until)
        if not days:
            return
        path = self._path(draw, days[-1]).selic
        spread = self.last_selic - float(to_annual(np.array([cdi.iloc[-1]]))[0])
        selic_days = [day for day in days if day in path]
        _, push = self._effects(draw, np.array([_day_number(d) for d in selic_days]))
        annual = np.maximum(
            np.array([path[day] for day in selic_days]) + push, SELIC_FLOOR
        )
        out[IndicatorSeries.SELIC] = pd.Series(
            np.round(to_daily(annual), 6), index=selic_days
        )
        cdi_annual = {
            day: rate - spread for day, rate in zip(selic_days, annual, strict=True)
        }
        cdi_days = [day for day in days if day > cdi_end]
        # Dia em que só o CDI falta (o real da SELIC já saiu) segue o último real
        out[IndicatorSeries.CDI] = pd.Series(
            np.round(
                to_daily(
                    np.array(
                        [
                            cdi_annual.get(day, self.last_selic - spread)
                            for day in cdi_days
                        ]
                    )
                ),
                6,
            ),
            index=cdi_days,
        )

    def _generate_ipca(
        self, draw: "_Draw", until: date, out: dict[IndicatorSeries, pd.Series]
    ) -> None:
        """O IPCA do mês sorteado mais o nível e os surtos do mês, em % ao mês."""
        months = [
            m for m in self._path(draw, until).ipca if _first_business_day(m) <= until
        ]
        if not months:
            return
        path = self._path(draw, until).ipca
        push, _ = self._effects(
            draw, np.array([_day_number(_first_business_day(m)) for m in months])
        )
        values = [
            path[m] + ((1 + added) ** (1 / MONTHS_PER_YEAR) - 1) * 100
            for m, added in zip(months, push, strict=True)
        ]
        out[IndicatorSeries.IPCA] = pd.Series(np.round(values, 2), index=months)


def _ramp(years: np.ndarray) -> np.ndarray:
    """Quanto da subida já aconteceu: de 0 a 1 em seis meses."""
    return np.minimum(years / SHOCK_RAMP_YEARS, 1.0)


def _decay(years: np.ndarray) -> np.ndarray:
    """O que resta de um pulso depois da subida: metade a cada ano."""
    return 0.5 ** (np.maximum(years - SHOCK_RAMP_YEARS, 0.0) / SHOCK_HALF_LIFE_YEARS)


@dataclass(frozen=True)
class _Draw:
    """Os controles de uma geração: nível e intensidade em fração, frequência em surtos por ano."""

    seed: int
    temperature: float
    level: float
    surge_frequency: float
    surge_intensity: float


@dataclass
class _Path:
    """Trecho de cada bloco e os níveis de SELIC (anual) e IPCA (% ao mês) sem nível nem surtos."""

    last_day: date
    chain: dict[int, int] = field(default_factory=dict)
    selic: dict[date, float] = field(default_factory=dict)
    ipca: dict[date, float] = field(default_factory=dict)
