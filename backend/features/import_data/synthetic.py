"""
Gerador de séries sintéticas: um futuro plausível para depois do último dia real.

Bootstrap em blocos conjunto: o futuro é montado com trechos reais de 60 pregões
do histórico, e o mesmo trecho vale para todos os ativos e indicadores no mesmo
dia. Crises, volatilidade que dura e setores andando juntos vêm do próprio
histórico. Os trechos se encadeiam por bioma (calmo, normal, agitado) com as
transições medidas no histórico, e a temperatura pesa o sorteio pela
volatilidade de cada trecho: em 1 o histórico como foi, abaixo favorece os
calmos, acima os agitados.

É uma conta pura sobre o histórico recebido: nada aqui lê ou grava no banco.
"""

import zlib
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from enum import IntEnum

import numpy as np
import pandas as pd

from backend.core.enum import IndicatorSeries
from backend.core.utils import business_days_between, next_business_day

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


def _months(after: date, until: date) -> list[date]:
    """Primeiro dia de cada mês depois do mês de `after`, até `until`."""
    months: list[date] = []
    year, month = after.year, after.month
    while True:
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
        first = date(year, month, 1)
        if first > until:
            return months
        months.append(first)


class SeriesGenerator:
    """
    Pré-calcula o histórico uma vez (calendário, trechos, biomas, retornos) para
    que gerações seguidas, como as de um preview, saiam baratas.
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

        self._chains: dict[tuple[int, float, Regime], dict[int, int]] = {}
        self._bars: dict[str, pd.DataFrame] = {}
        self._returns: dict[str, np.ndarray] = {}
        self._group_means: dict[tuple[str, str], np.ndarray] = {}

    def generate(
        self,
        until: date,
        seed: int,
        temperature: float = 1.0,
        start_regime: Regime | None = None,
        tickers: Iterable[str] | None = None,
    ) -> GeneratedSeries:
        """
        Cada série recebe os dias úteis desde o dia seguinte ao seu último dado
        real até `until`. O trecho sorteado para cada data depende só da semente,
        da temperatura, do bioma inicial e da data: gerar um ativo sozinho dá as
        mesmas linhas que gerá-lo junto com os outros.
        """
        if not MIN_TEMPERATURE <= temperature <= MAX_TEMPERATURE:
            raise ValueError(
                f"Temperatura fora de [{MIN_TEMPERATURE}, {MAX_TEMPERATURE}]."
            )
        draw = _Draw(
            seed,
            temperature,
            self.current_regime if start_regime is None else start_regime,
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
    # Sorteio dos trechos

    def _chain(self, draw: "_Draw", last_block: int) -> dict[int, int]:
        """Início do trecho de cada bloco, da âncora até `last_block`."""
        key = (draw.seed, draw.temperature, draw.start_regime)
        chain = self._chains.setdefault(key, {})
        if chain and max(chain) >= last_block:
            return chain

        relative = self.block_vol / np.median(self.block_vol)
        weights = relative ** (TEMPERATURE_STEEPNESS * (draw.temperature - 1))
        within = [np.cumsum(weights[m] / weights[m].sum()) for m in self.members]
        # A temperatura também inclina as transições para os biomas mais pesados
        tilted = self.transitions * np.array([weights[m].mean() for m in self.members])
        tilted = np.cumsum(tilted / tilted.sum(axis=1, keepdims=True), axis=1)

        state = draw.start_regime
        for block in range(self.anchor_block, last_block + 1):
            u_regime, u_block = np.random.default_rng([draw.seed, block]).random(2)
            if block > self.anchor_block:
                state = Regime(int(min(np.searchsorted(tilted[state], u_regime), 2)))
            i = min(np.searchsorted(within[state], u_block), len(within[state]) - 1)
            chain[block] = int(self.starts[self.members[state][i]])
        return chain

    def _sources(self, draw: "_Draw", days: list[date]) -> np.ndarray:
        """Posição no calendário do sorteio do pregão real que cada dia copia."""
        blocks = [_block_of(day) for day in days]
        chain = self._chain(draw, max(b for b, _ in blocks))
        return np.array([chain[max(b, self.anchor_block)] + off for b, off in blocks])

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
        indicators = self.indicators

        # Ibovespa: pontos, como o fechamento de um ativo
        ibov = indicators[IndicatorSeries.IBOV]
        days = _business_days(_last_day(ibov), until)
        if days:
            moves = self.market[self._sources(draw, days)]
            out[IndicatorSeries.IBOV] = pd.Series(
                float(ibov.iloc[-1]) * np.exp(np.cumsum(moves)), index=days
            )

        selic = indicators.get(IndicatorSeries.SELIC)
        cdi = indicators.get(IndicatorSeries.CDI)
        if selic is not None and cdi is not None:
            self._generate_rates(draw, until, selic, cdi, out)

        ipca = indicators.get(IndicatorSeries.IPCA)
        if ipca is not None:
            self._generate_ipca(draw, until, ipca, out)

    def _generate_rates(
        self,
        draw: "_Draw",
        until: date,
        selic: pd.Series,
        cdi: pd.Series,
        out: dict[IndicatorSeries, pd.Series],
    ) -> None:
        """
        A SELIC é nível: parte do último valor real e soma as variações dos
        trechos sorteados, presa ao mínimo e ao máximo desde POOL_START. O CDI
        anda colado nela, com o spread do último dia real.
        """
        annual = _to_annual(selic.reindex(self.calendar, method="ffill").to_numpy())
        changes = np.nan_to_num(np.diff(annual, prepend=np.nan))
        floor, ceiling = np.nanmin(annual), np.nanmax(annual)

        selic_end, cdi_end = _last_day(selic), _last_day(cdi)
        days = _business_days(min(selic_end, cdi_end), until)
        if not days:
            return
        level = float(_to_annual(np.array([selic.iloc[-1]]))[0])
        spread = level - float(_to_annual(np.array([cdi.iloc[-1]]))[0])
        path = np.empty(len(days))
        for j, source in enumerate(self._sources(draw, days)):
            level = min(max(level + changes[source], floor), ceiling)
            path[j] = level

        for series, end, annual_path in (
            (IndicatorSeries.SELIC, selic_end, path),
            (IndicatorSeries.CDI, cdi_end, path - spread),
        ):
            after = np.array([day > end for day in days])
            out[series] = pd.Series(
                np.round(_to_daily(annual_path[after]), 6),
                index=[day for day in days if day > end],
            )

    def _generate_ipca(
        self,
        draw: "_Draw",
        until: date,
        ipca: pd.Series,
        out: dict[IndicatorSeries, pd.Series],
    ) -> None:
        """
        O IPCA de cada mês gerado é o do mês sorteado para o primeiro dia útil
        dele: a inflação mensal oscila em torno de uma média e não acumula.
        """
        months = _months(_last_day(ipca), until)
        if not months:
            return
        first_days = [m if m.weekday() < 5 else next_business_day(m) for m in months]
        by_month = dict(zip(_dates(ipca.index), ipca.to_numpy(), strict=True))
        last = float(ipca.iloc[-1])
        values = [
            by_month.get(self.calendar_days[source].replace(day=1), last)
            for source in self._sources(draw, first_days)
        ]
        out[IndicatorSeries.IPCA] = pd.Series(np.round(values, 2), index=months)


@dataclass(frozen=True)
class _Draw:
    seed: int
    temperature: float
    start_regime: Regime
