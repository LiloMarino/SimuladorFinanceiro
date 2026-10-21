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

Choque de inflação: uma camada por cima do sorteio, que sobe em seis meses e
decai pela metade a cada ano. Soma X pontos à inflação anual, 1,5·X à SELIC
(princípio de Taylor: o juro sobe mais que a inflação) e, à bolsa, a reação
histórica do Ibovespa à SELIC, cada ativo pelo seu beta.

É uma conta pura sobre o histórico recebido: nada aqui lê ou grava no banco.
"""

import zlib
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import IntEnum

import numpy as np
import pandas as pd

from backend.core.enum import IndicatorSeries
from backend.core.utils import (
    business_days_between,
    next_business_day,
    subtract_months,
)

BLOCK_DAYS = 60
TRADING_DAYS_PER_YEAR = 252
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
# Choque de inflação, em pontos percentuais da inflação anual
MIN_INFLATION_SHOCK, MAX_INFLATION_SHOCK = -5.0, 20.0
SHOCK_RAMP_YEARS, SHOCK_HALF_LIFE_YEARS = 0.5, 1.0
SELIC_SHOCK_RESPONSE = 1.5
SELIC_FLOOR = 0.005
QUARTER_DAYS = 63

PRICE_COLUMNS = ["open", "high", "low", "close", "volume"]


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


@dataclass(frozen=True)
class MarketHistory:
    """
    Toda a base real. Indicadores como o Banco Central publica: CDI e SELIC em %
    ao dia útil, IPCA em % ao mês datado no dia 1, IBOV em pontos.
    """

    assets: dict[str, AssetHistory]
    indicators: dict[IndicatorSeries, pd.Series]


@dataclass(frozen=True)
class GeneratedSeries:
    """Linhas geradas, no mesmo formato da entrada, prontas para gravar como geradas."""

    assets: dict[str, pd.DataFrame] = field(default_factory=dict)
    indicators: dict[IndicatorSeries, pd.Series] = field(default_factory=dict)


def _clean(returns: np.ndarray) -> np.ndarray:
    out = returns.copy()
    out[(out > MAX_DAILY_UP) | (out < MAX_DAILY_DOWN)] = np.nan
    return out


def _to_annual(daily_pct: np.ndarray) -> np.ndarray:
    return (1 + daily_pct / 100) ** TRADING_DAYS_PER_YEAR - 1


def _to_daily(annual: np.ndarray) -> np.ndarray:
    return ((1 + annual) ** (1 / TRADING_DAYS_PER_YEAR) - 1) * 100


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
        # O choque começa no primeiro dia depois do último pregão real
        self.shock_start = _day_number(self.calendar_days[-1]) + 1
        self._prepare_economy()

        self._paths: dict[tuple[int, float, Regime], _Path] = {}
        self._bars: dict[str, pd.DataFrame] = {}
        self._returns: dict[str, np.ndarray] = {}
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
            self.selic_annual = _to_annual(
                selic.reindex(self.calendar, method="ffill").to_numpy()
            )
            self.last_selic = float(_to_annual(np.array([selic.iloc[-1]]))[0])
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
        start_regime: Regime | None = None,
        inflation_shock: float = 0.0,
        tickers: Iterable[str] | None = None,
    ) -> GeneratedSeries:
        """
        Cada série recebe os dias úteis desde o dia seguinte ao seu último dado
        real até `until`. O trecho sorteado para cada data depende só da semente,
        da temperatura, do bioma inicial e da data: gerar um ativo sozinho dá as
        mesmas linhas que gerá-lo junto com os outros. O choque de inflação, em
        pontos percentuais, muda os níveis sem mudar os trechos.
        """
        if not MIN_TEMPERATURE <= temperature <= MAX_TEMPERATURE:
            raise ValueError(
                f"Temperatura fora de [{MIN_TEMPERATURE}, {MAX_TEMPERATURE}]."
            )
        if not MIN_INFLATION_SHOCK <= inflation_shock <= MAX_INFLATION_SHOCK:
            raise ValueError(
                "Choque de inflação fora de "
                f"[{MIN_INFLATION_SHOCK}, {MAX_INFLATION_SHOCK}] pontos."
            )
        draw = _Draw(
            seed,
            temperature,
            self.current_regime if start_regime is None else start_regime,
            inflation_shock / 100,
        )
        selected = self.history.assets if tickers is None else tickers
        result = GeneratedSeries()
        for ticker in selected:
            bars = self._generate_asset(draw, ticker, until)
            if bars is not None:
                result.assets[ticker] = bars
        self._generate_indicators(draw, until, result.indicators)
        return result

    # ------------------------------------------------------------------
    # Sorteio dos trechos e caminho da economia

    def _path(self, draw: "_Draw", last_day: date) -> "_Path":
        """
        Percorre os dias desde o bloco âncora sorteando um trecho por bloco e
        levando junto a SELIC e o IPCA sem choque: o encaixe do próximo trecho
        depende do estado a que os anteriores levaram.
        """
        key = (draw.seed, draw.temperature, draw.start_regime)
        cached = self._paths.get(key)
        if cached is not None and cached.last_day >= last_day:
            return cached

        relative = self.block_vol / np.median(self.block_vol)
        heat = relative ** (TEMPERATURE_STEEPNESS * (draw.temperature - 1))
        path = _Path(last_day)
        level = self.last_selic
        recent_ipca = list(self.last_ipca)
        ipca12 = [_accumulated(recent_ipca)] * 4 if recent_ipca else [np.nan] * 4
        regime = draw.start_regime

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

    def _shock(self, draw: "_Draw", day: date) -> float:
        """Choque vigente no dia: sobe em seis meses e decai pela metade a cada ano."""
        if not draw.shock:
            return 0.0
        years = max(_day_number(day) - self.shock_start, 0) / TRADING_DAYS_PER_YEAR
        ramp = min(years / SHOCK_RAMP_YEARS, 1.0)
        decay = 0.5 ** (max(years - SHOCK_RAMP_YEARS, 0) / SHOCK_HALF_LIFE_YEARS)
        return draw.shock * ramp * decay

    def _shock_moves(self, draw: "_Draw", days: list[date]) -> np.ndarray:
        """Retorno extra do Ibovespa em cada dia pela SELIC que o choque empurrou."""
        if not draw.shock:
            return np.zeros(len(days))
        previous = _day_from_number(_day_number(days[0]) - 1)
        selic_push = SELIC_SHOCK_RESPONSE * np.array(
            [self._shock(draw, d) for d in [previous, *days]]
        )
        return self.market_selic_beta * np.diff(selic_push)

    # ------------------------------------------------------------------
    # Ativos

    def _asset_bars(self, ticker: str) -> pd.DataFrame:
        if ticker not in self._bars:
            self._bars[ticker] = _by_datetime(self.history.assets[ticker].bars)
        return self._bars[ticker]

    def _asset_returns(self, ticker: str) -> np.ndarray:
        if ticker not in self._returns:
            close = self._asset_bars(ticker)["close"]
            levels = close.reindex(self.calendar).to_numpy()
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
    ) -> pd.DataFrame | None:
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
        median_volume = bars["volume"].rolling(TRADING_DAYS_PER_YEAR, min_periods=20)
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

        # O choque chega ao ativo pelo beta dele contra o Ibovespa
        market_beta = next((b for ref, b, _ in fits if ref is self.market), 1.0)
        generated += market_beta * self._shock_moves(draw, days)

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
        recent_volume = float(bars["volume"].iloc[-TRADING_DAYS_PER_YEAR:].median())
        volume = np.round(
            volume_ratio.fillna(1.0).to_numpy()[ratio_day] * recent_volume
        ).astype(np.int64)
        return pd.DataFrame(
            {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
            index=pd.Index(days, name="date"),
        )

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
            moves = moves + self._shock_moves(draw, days)
            out[IndicatorSeries.IBOV] = pd.Series(
                float(ibov.iloc[-1]) * np.exp(np.cumsum(moves)), index=days
            )

        selic = self.indicators.get(IndicatorSeries.SELIC)
        cdi = self.indicators.get(IndicatorSeries.CDI)
        if selic is not None and cdi is not None:
            self._generate_rates(draw, until, selic, cdi, out)
        if self.ipca_end is not None:
            self._generate_ipca(draw, until, out)

    def _generate_rates(
        self,
        draw: "_Draw",
        until: date,
        selic: pd.Series,
        cdi: pd.Series,
        out: dict[IndicatorSeries, pd.Series],
    ) -> None:
        """
        A SELIC do caminho mais o empurrão do choque; o CDI anda colado nela,
        com o spread do último dia real.
        """
        cdi_end = _last_day(cdi)
        days = _business_days(min(_last_day(selic), cdi_end), until)
        if not days:
            return
        path = self._path(draw, days[-1]).selic
        spread = self.last_selic - float(_to_annual(np.array([cdi.iloc[-1]]))[0])
        selic_days = [day for day in days if day in path]
        annual = np.array(
            [
                max(
                    path[day] + SELIC_SHOCK_RESPONSE * self._shock(draw, day),
                    SELIC_FLOOR,
                )
                for day in selic_days
            ]
        )
        out[IndicatorSeries.SELIC] = pd.Series(
            np.round(_to_daily(annual), 6), index=selic_days
        )
        cdi_annual = {
            day: rate - spread for day, rate in zip(selic_days, annual, strict=True)
        }
        cdi_days = [day for day in days if day > cdi_end]
        # Dia em que só o CDI falta (o real da SELIC já saiu) segue o último real
        out[IndicatorSeries.CDI] = pd.Series(
            np.round(
                _to_daily(
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
        """O IPCA do mês sorteado mais o choque do mês, convertido para % ao mês."""
        months = [
            m for m in self._path(draw, until).ipca if _first_business_day(m) <= until
        ]
        if not months:
            return
        path = self._path(draw, until).ipca
        values = [
            path[m]
            + ((1 + self._shock(draw, _first_business_day(m))) ** (1 / 12) - 1) * 100
            for m in months
        ]
        out[IndicatorSeries.IPCA] = pd.Series(np.round(values, 2), index=months)


@dataclass(frozen=True)
class _Draw:
    seed: int
    temperature: float
    start_regime: Regime
    shock: float


@dataclass
class _Path:
    """Trecho de cada bloco e os níveis sem choque de SELIC (anual) e IPCA (% ao mês)."""

    last_day: date
    chain: dict[int, int] = field(default_factory=dict)
    selic: dict[date, float] = field(default_factory=dict)
    ipca: dict[date, float] = field(default_factory=dict)
