"""
Medidas do jogador que as conquistas usam. Uma métrica é um número calculado a partir
da partida; várias conquistas podem apontar para a mesma, com metas diferentes.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum
from functools import cached_property

from backend.core import repository
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.snapshot import SnapshotDTO
from backend.core.enum import GameType, PlayerGrouping
from backend.core.utils import next_business_day
from backend.features.statistics import returns, risk, score
from backend.features.variable_income.income_tax import MonthlyTax
from backend.features.variable_income.price_impact import (
    AVERAGE_VOLUME_WINDOW,
    impact,
)

ZERO = Decimal(0)
ONE = Decimal(1)

# Pregões em 12 meses
YEAR_OF_TRADING_DAYS = 252
# Queda do Ibovespa, a partir do pico, que conta como "queda" e como "tempestade"
DOWNTURN_DEPTH = Decimal("0.20")
STORM_DEPTH = Decimal("0.30")
# Caixa abaixo desta fração do patrimônio conta como tudo investido
FULLY_INVESTED_CASH_SHARE = Decimal("0.01")
# Deslocamento do preço, em fração, a partir do qual a ordem do jogador "mexeu no mercado"
MARKET_MOVE = 0.005
# Dias corridos lidos para trás ao procurar a ordem que moveu o preço: cobrem o intervalo
# entre o dia da ordem e o pregão em que o avaliador a vê
MARKET_MOVE_LOOKBACK_DAYS = 7


class Trigger(Enum):
    """
    Quando a métrica é calculada. O custo de avaliar cresce com as métricas de cada
    gatilho, não com o número de conquistas.
    """

    # Todo pregão, só com o snapshot do dia
    TICK = "TICK"
    # No pregão em que o jogador deu ordens, que são os eventos novos
    ORDER = "ORDER"
    # Na virada do mês, sobre o histórico inteiro
    MONTH = "MONTH"
    # Quando a partida acaba
    MATCH_END = "MATCH_END"


@dataclass(frozen=True)
class MatchResult:
    """Como a partida terminou, para as métricas do gatilho `MATCH_END`."""

    # Quem venceu: em equipes, todos os membros da equipe vencedora
    winners: frozenset[int]
    players_count: int
    # A partida acabou porque alguém chegou à meta, e não pela data final
    ended_by_goal: bool


# Contexto fora do fim da partida: ninguém venceu ainda
NO_MATCH = MatchResult(winners=frozenset(), players_count=0, ended_by_goal=False)


def no_income_tax(_user_id: int) -> list[MonthlyTax]:
    return []


def no_market_end() -> date | None:
    return None


@dataclass(frozen=True)
class Sources:
    """Leituras que dependem da partida em andamento e valem para todos os jogadores."""

    # Apuração mensal do IR de um jogador, como o motor a calcula
    income_tax: Callable[[int], list[MonthlyTax]] = no_income_tax
    # Último pregão com dado real; None sem mercado real
    market_real_end: Callable[[], date | None] = no_market_end


NO_SOURCES = Sources()


@dataclass(eq=False)
class Context:
    """O jogador no pregão avaliado; o que as métricas lêem do banco é lido uma vez."""

    user_id: int
    settings: SimulationDTO
    snapshot: SnapshotDTO
    match: MatchResult = NO_MATCH
    sources: Sources = NO_SOURCES
    _values: dict[str, Decimal] = field(default_factory=dict)

    @property
    def today(self) -> date:
        return self.snapshot.snapshot_date

    @cached_property
    def history(self) -> list[PatrimonialHistoryDTO]:
        return repository.portfolio.get_patrimonial_history(self.user_id)

    @cached_property
    def days(self) -> risk.DailyReturns:
        return risk.daily_returns(self.history)

    @cached_property
    def won(self) -> bool:
        return self.user_id in self.match.winners

    @cached_property
    def won_against_others(self) -> bool:
        """Venceu com pelo menos mais um jogador na partida."""
        return self.won and self.match.players_count >= 2

    def buy_dates(self) -> list[date]:
        return repository.achievements.equity_order_dates(
            self.settings.id, self.user_id, "BUY"
        )

    def sell_dates(self) -> list[date]:
        return repository.achievements.equity_order_dates(
            self.settings.id, self.user_id, "SELL"
        )

    def value(self, name: str) -> Decimal:
        """Valor da métrica `name` neste contexto."""
        if name not in self._values:
            self._values[name] = METRICS[name].compute(self)
        return self._values[name]


@dataclass(frozen=True)
class Metric:
    name: str
    when: Trigger
    compute: Callable[[Context], Decimal]


METRICS: dict[str, Metric] = {}


def metric(name: str, when: Trigger):
    """Registra a função como a métrica `name`, calculada no gatilho `when`."""

    def register(compute: Callable[[Context], Decimal]):
        METRICS[name] = Metric(name, when, compute)
        return compute

    return register


def _flag(condition: bool) -> Decimal:
    return ONE if condition else ZERO


# --------------------------------------------------
# TICK: só o snapshot do dia
# --------------------------------------------------


@metric("networth", Trigger.TICK)
def networth(ctx: Context) -> Decimal:
    return ctx.snapshot.total_networth


@metric("capital_multiple", Trigger.TICK)
def capital_multiple(ctx: Context) -> Decimal:
    """Quantas vezes o patrimônio é o que o jogador colocou: saldo inicial mais aportes."""
    provided = ctx.settings.starting_cash + ctx.snapshot.total_contribution
    return ctx.snapshot.total_networth / provided if provided > 0 else ZERO


@metric("fully_invested", Trigger.TICK)
def fully_invested(ctx: Context) -> Decimal:
    snap = ctx.snapshot
    invested = snap.total_equity + snap.total_fixed
    return _flag(
        snap.total_networth > 0
        and invested > 0
        and 0 <= snap.total_cash < snap.total_networth * FULLY_INVESTED_CASH_SHARE
    )


@metric("beyond_horizon", Trigger.TICK)
def beyond_horizon(ctx: Context) -> Decimal:
    """Hoje está depois do último pregão com dado real: o mercado daqui em diante é gerado."""
    real_end = ctx.sources.market_real_end()
    return _flag(real_end is not None and ctx.today > real_end)


@metric("candle_challenge_hits", Trigger.TICK)
def candle_challenge_hits(ctx: Context) -> Decimal:
    """Acertos do jogador no desafio da vela do lobby, somando todas as rodadas."""
    return Decimal(repository.candle_challenge.total_hits(ctx.user_id))


# --------------------------------------------------
# ORDER: os eventos da partida
# --------------------------------------------------


@metric("equity_buys", Trigger.ORDER)
def equity_buys(ctx: Context) -> Decimal:
    return Decimal(
        repository.achievements.equity_orders(ctx.settings.id, ctx.user_id, "BUY")
    )


@metric("equity_sells", Trigger.ORDER)
def equity_sells(ctx: Context) -> Decimal:
    return Decimal(
        repository.achievements.equity_orders(ctx.settings.id, ctx.user_id, "SELL")
    )


@metric("fixed_income_buys", Trigger.ORDER)
def fixed_income_buys(ctx: Context) -> Decimal:
    return Decimal(
        repository.achievements.fixed_income_buys(ctx.settings.id, ctx.user_id)
    )


@metric("order_count", Trigger.ORDER)
def order_count(ctx: Context) -> Decimal:
    equity = repository.achievements.equity_orders(ctx.settings.id, ctx.user_id, None)
    return Decimal(equity) + ctx.value("fixed_income_buys")


@metric("held_assets", Trigger.ORDER)
def held_assets(ctx: Context) -> Decimal:
    return Decimal(repository.achievements.held_assets(ctx.settings.id, ctx.user_id))


@metric("held_sectors", Trigger.ORDER)
def held_sectors(ctx: Context) -> Decimal:
    return Decimal(repository.achievements.held_sectors(ctx.settings.id, ctx.user_id))


@metric("day_traded", Trigger.ORDER)
def day_traded(ctx: Context) -> Decimal:
    return _flag(
        repository.achievements.day_traded_assets(ctx.settings.id, ctx.user_id) > 0
    )


@metric("moved_market", Trigger.ORDER)
def moved_market(ctx: Context) -> Decimal:
    """
    Uma ordem do jogador, sozinha, deslocou o preço de um ativo em `MARKET_MOVE` ou mais.
    O deslocamento é o do impacto de preço (quantidade líquida do dia sobre o volume
    médio), então só existe na partida com o impacto ligado.
    """
    settings = ctx.settings
    if not settings.price_impact_enabled:
        return ZERO
    since = ctx.today - timedelta(days=MARKET_MOVE_LOOKBACK_DAYS)
    for ticker, day, quantity in repository.achievements.equity_flows(
        settings.id, ctx.user_id, since
    ):
        average_volume = repository.stock.get_average_volume(
            ticker, day, AVERAGE_VOLUME_WINDOW, simulation_id=settings.id
        )
        if (
            abs(impact(quantity, average_volume, settings.price_impact_k))
            >= MARKET_MOVE
        ):
            return ONE
    return ZERO


@metric("bought_on_first_day", Trigger.ORDER)
def bought_on_first_day(ctx: Context) -> Decimal:
    first_day = next_business_day(ctx.settings.start_date - timedelta(days=1))
    return _flag(any(day <= first_day for day in ctx.buy_dates()))


# --------------------------------------------------
# MONTH: o histórico inteiro
# --------------------------------------------------


@metric("months_above_cdi", Trigger.MONTH)
def months_above_cdi(ctx: Context) -> Decimal:
    """Meses fechados seguidos, até o último, em que o jogador rendeu mais que o CDI."""
    current_month = ctx.today.replace(day=1)
    closed = [m for m in risk.monthly_returns(ctx.days) if m.month < current_month]
    streak = 0
    for month in reversed(closed):
        if month.value <= month.cdi:
            break
        streak += 1
    return Decimal(streak)


@metric("beat_ibov_year", Trigger.MONTH)
def beat_ibov_year(ctx: Context) -> Decimal:
    """Nos últimos 12 meses a cota do jogador subiu mais que o Ibovespa."""
    window = ctx.history[-(YEAR_OF_TRADING_DAYS + 1) :]
    if len(window) <= YEAR_OF_TRADING_DAYS:
        return ZERO
    ibov = returns.ibov_cumulative([h.snapshot_date for h in window])
    if not ibov:
        return ZERO
    quota = returns.cumulative_returns(window, risk.daily_returns(window))
    return _flag(quota[-1][1] > ibov[-1][1])


@metric("exempt_month", Trigger.MONTH)
def exempt_month(ctx: Context) -> Decimal:
    """Fechou um mês com ganho em ações isento, por vender abaixo do teto, e sem imposto."""
    current_month = (ctx.today.year, ctx.today.month)
    return _flag(
        any(
            (m.year, m.month) < current_month
            and m.stock_exempt_profit > 0
            and m.tax == 0
            for m in ctx.sources.income_tax(ctx.user_id)
        )
    )


@metric("overall_score", Trigger.MONTH)
def overall_score(ctx: Context) -> Decimal:
    """Nota geral do jogador hoje; zero antes dos pregões que a nota exige."""
    player_score = score.player_score(ctx.history)
    return player_score.total if player_score else ZERO


@metric("days_without_selling", Trigger.MONTH)
def days_without_selling(ctx: Context) -> Decimal:
    """Dias desde a última venda (ou a primeira compra, se nunca vendeu); 0 sem ter comprado."""
    buys = ctx.buy_dates()
    if not buys:
        return ZERO
    sells = ctx.sell_dates()
    since = max(buys[0], sells[-1]) if sells else buys[0]
    return Decimal((ctx.today - since).days)


@dataclass(frozen=True)
class Downturn:
    """Queda do Ibovespa: do pico até o fundo, e o dia em que passou da profundidade pedida."""

    peak: date
    reached: date
    trough: date
    depth: Decimal


def ibov_downturns(dates: list[date], depth: Decimal) -> list[Downturn]:
    """As quedas do Ibovespa de pelo menos `depth` (0.20 = 20%) a partir de um pico."""
    cumulative = returns.ibov_cumulative(dates)
    if not cumulative:
        return []

    found: list[Downturn] = []
    peak_day, peak = cumulative[0][0], 1 + cumulative[0][1]
    reached: date | None = None
    trough_day, trough = peak_day, peak
    for day, cum in cumulative[1:]:
        level = 1 + cum
        # Um novo pico fecha a queda anterior, se ela chegou à profundidade
        if level >= peak:
            if reached is not None:
                found.append(
                    Downturn(peak_day, reached, trough_day, (peak - trough) / peak)
                )
            peak_day, peak, reached = day, level, None
            trough_day, trough = day, level
            continue
        if level < trough:
            trough_day, trough = day, level
        if reached is None and (peak - level) / peak >= depth:
            reached = day
    if reached is not None:
        found.append(Downturn(peak_day, reached, trough_day, (peak - trough) / peak))
    return found


def _ibov_downturns(ctx: Context, depth: Decimal) -> list[Downturn]:
    return ibov_downturns([h.snapshot_date for h in ctx.history], depth)


@metric("held_through_downturn", Trigger.MONTH)
def held_through_downturn(ctx: Context) -> Decimal:
    """Tinha ações antes do pico de uma queda do Ibovespa e não vendeu nenhuma até o fundo."""
    buys, sells = ctx.buy_dates(), ctx.sell_dates()
    return _flag(
        any(
            buys
            and buys[0] <= d.peak
            and not any(d.peak <= sell <= d.trough for sell in sells)
            for d in _ibov_downturns(ctx, DOWNTURN_DEPTH)
        )
    )


@metric("bought_in_downturn", Trigger.MONTH)
def bought_in_downturn(ctx: Context) -> Decimal:
    buys = ctx.buy_dates()
    return _flag(
        any(
            d.reached <= buy <= d.trough
            for d in _ibov_downturns(ctx, DOWNTURN_DEPTH)
            for buy in buys
        )
    )


@metric("outperformed_storm", Trigger.MONTH)
def outperformed_storm(ctx: Context) -> Decimal:
    """Numa queda de 30% do Ibovespa, a cota do jogador caiu menos que o índice."""
    storms = _ibov_downturns(ctx, STORM_DEPTH)
    if not storms:
        return ZERO
    quota = {
        day: 1 + cum for day, cum in returns.cumulative_returns(ctx.history, ctx.days)
    }
    for storm in storms:
        if storm.peak not in quota or storm.trough not in quota:
            continue
        peak, trough = quota[storm.peak], quota[storm.trough]
        if (peak - trough) / peak < storm.depth:
            return ONE
    return ZERO


# --------------------------------------------------
# MATCH_END: o resultado da partida
# --------------------------------------------------


@metric("matches_won", Trigger.MATCH_END)
def matches_won(ctx: Context) -> Decimal:
    return _flag(ctx.won_against_others)


@metric("won_expert_mode", Trigger.MATCH_END)
def won_expert_mode(ctx: Context) -> Decimal:
    return _flag(ctx.won_against_others and ctx.settings.expert_mode)


@metric("won_as_team", Trigger.MATCH_END)
def won_as_team(ctx: Context) -> Decimal:
    return _flag(
        ctx.won_against_others and ctx.settings.player_grouping is PlayerGrouping.TEAMS
    )


@metric("won_room_size", Trigger.MATCH_END)
def won_room_size(ctx: Context) -> Decimal:
    return Decimal(ctx.match.players_count) if ctx.won else ZERO


@metric("finished_to_end", Trigger.MATCH_END)
def finished_to_end(ctx: Context) -> Decimal:
    return _flag(not ctx.match.ended_by_goal)


@metric("won_goal_race", Trigger.MATCH_END)
def won_goal_race(ctx: Context) -> Decimal:
    return _flag(
        ctx.won
        and ctx.match.ended_by_goal
        and ctx.settings.game_type is GameType.GOAL_RACE
    )


@metric("won_financial_independence", Trigger.MATCH_END)
def won_financial_independence(ctx: Context) -> Decimal:
    return _flag(
        ctx.won
        and ctx.match.ended_by_goal
        and ctx.settings.game_type is GameType.FINANCIAL_INDEPENDENCE
    )
