"""
Cada aba do relatório montada a partir do banco, para uma ou mais simulações
salvas: a partida em andamento, o fechamento e a comparação leem o mesmo caminho.
"""

from collections.abc import Callable
from datetime import date
from decimal import Decimal
from functools import cache

from backend.core import repository
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.dto.statistics_report import (
    BenchmarkDTO,
    BenchmarkSeries,
    CompositionReportDTO,
    OperationsReportDTO,
    OverviewReportDTO,
    PlayerCompositionDTO,
    PlayerOperationsDTO,
    PlayerReturnsDTO,
    PlayerRiskDTO,
    ReturnsReportDTO,
    RiskReportDTO,
    SeriesPointDTO,
)
from backend.core.enum import EquityEventType, VictoryCriterion
from backend.core.sectors import allocate_by_sector
from backend.features.statistics import operations, returns, risk, sectors
from backend.features.statistics.ranking import build_overview, capital_provided
from backend.features.variable_income.broker import to_money
from backend.features.variable_income.price_impact import PriceImpact


def build_overview_report(simulation_ids: list[int]) -> OverviewReportDTO:
    return build_overview(
        repository.statistics.get_players_history(simulation_ids),
        _shared_criterion(simulation_ids),
    )


def _shared_criterion(simulation_ids: list[int]) -> VictoryCriterion:
    """O critério das simulações quando todas usam o mesmo; senão, a nota geral."""
    simulations = [repository.simulation.get_simulation(i) for i in simulation_ids]
    criteria = {s.victory_criterion for s in simulations if s is not None}
    return criteria.pop() if len(criteria) == 1 else VictoryCriterion.SCORE


def build_returns_report(simulation_ids: list[int]) -> ReturnsReportDTO:
    players = repository.statistics.get_players_history(simulation_ids)

    entries = []
    for player in players:
        days = risk.daily_returns(player.history)
        months = risk.monthly_returns(days)
        entries.append(
            PlayerReturnsDTO(
                **_ref(player),
                networth=[
                    SeriesPointDTO(date=h.snapshot_date, value=h.total_networth)
                    for h in player.history
                ],
                cumulative_return=_points(
                    returns.cumulative_returns(player.history, days)
                ),
                capital_provided=capital_provided(player),
                annual_return=risk.annual_return(days),
                months_above_cdi=sum(1 for m in months if m.value > m.cdi),
                positive_months=sum(1 for m in months if m.value > 0),
                months=len(months),
            )
        )

    benchmarks = []
    for simulation_id, simulation_name, dates in _simulation_dates(players):
        references: list[tuple[BenchmarkSeries, risk.DailyReturns]] = [
            ("CDI", returns.cdi_cumulative(dates)),
            ("IBOV", returns.ibov_cumulative(dates)),
        ]
        for series, cumulative in references:
            if cumulative:
                benchmarks.append(
                    BenchmarkDTO(
                        series=series,
                        simulation_id=simulation_id,
                        simulation_name=simulation_name,
                        cumulative_return=_points(cumulative),
                        annual_return=returns.annualize(cumulative),
                    )
                )

    return ReturnsReportDTO(players=entries, benchmarks=benchmarks)


def build_risk_report(simulation_ids: list[int]) -> RiskReportDTO:
    entries = []
    for player in repository.statistics.get_players_history(simulation_ids):
        days = risk.daily_returns(player.history)
        volatility = risk.annual_volatility([r for _, r in days])
        months = risk.monthly_returns(days)
        entries.append(
            PlayerRiskDTO(
                **_ref(player),
                drawdown=_points(risk.drawdown_series(days)),
                rolling_volatility=_points(risk.rolling_volatility(days)),
                max_drawdown=risk.max_drawdown(days),
                annual_volatility=volatility,
                sharpe_ratio=risk.sharpe_ratio(days, volatility),
                sortino_ratio=risk.sortino_ratio(days),
                time_underwater=risk.time_underwater(days),
                worst_month=min((m.value for m in months), default=None),
                annual_return=risk.annual_return(days),
                days=len(days),
            )
        )
    return RiskReportDTO(players=entries, rolling_window=risk.ROLLING_WINDOW)


def build_composition_report(simulation_ids: list[int]) -> CompositionReportDTO:
    players = repository.statistics.get_players_history(simulation_ids)
    trades = repository.statistics.get_players_trades(simulation_ids)
    classification = repository.stock.get_classification()
    price_impact = _price_impacts()

    entries = []
    for player in players:
        player_trades = trades.get((player.simulation_id, player.player_nickname), [])
        prices = _last_day_prices(
            player_trades,
            player.history[-1].snapshot_date,
            price_impact(player.simulation_id),
        )
        allocation = allocate_by_sector(
            sectors.position_values(player_trades, prices), classification
        )
        entries.append(
            PlayerCompositionDTO(
                **_ref(player),
                history=player.history,
                sectors=allocation,
                effective_sectors=sectors.effective_sectors(allocation),
                sector_profit=sectors.sector_profit(
                    player_trades, prices, classification
                ),
            )
        )
    return CompositionReportDTO(players=entries)


def build_operations_report(simulation_ids: list[int]) -> OperationsReportDTO:
    players = repository.statistics.get_players_history(simulation_ids)
    trades = repository.statistics.get_players_trades(simulation_ids)
    taxes = repository.statistics.get_players_tax(simulation_ids)
    price_impact = _price_impacts()

    entries = []
    for player in players:
        key = (player.simulation_id, player.player_nickname)
        player_trades = trades.get(key, [])
        entries.append(
            PlayerOperationsDTO(
                **_ref(player),
                buy_trades=sum(
                    1 for t in player_trades if t.event_type is EquityEventType.BUY
                ),
                sell_trades=sum(
                    1 for t in player_trades if t.event_type is EquityEventType.SELL
                ),
                traded_volume=operations.traded_volume(player_trades),
                turnover=operations.turnover(player_trades, player.history),
                income_tax_paid=taxes.get(key, Decimal(0)),
                impact_cost=operations.impact_cost(
                    player_trades, price_impact(player.simulation_id)
                ),
                monthly_volume=operations.monthly_volume(player_trades),
            )
        )
    return OperationsReportDTO(players=entries)


def _ref(player: PlayerHistoryDTO) -> dict:
    return {
        "player_nickname": player.player_nickname,
        "simulation_id": player.simulation_id,
        "simulation_name": player.simulation_name,
    }


def _points(series: risk.DailyReturns) -> list[SeriesPointDTO]:
    return [SeriesPointDTO(date=day, value=value) for day, value in series]


def _last_day_prices(trades, day: date, impact: PriceImpact) -> dict[str, Decimal]:
    """Preço de cada ativo em carteira no dia, como a partida o via: o histórico x o fator."""
    held = sectors.final_quantities(trades)
    if not held:
        return {}
    closes = repository.stock.get_closes_on(day)
    return {
        ticker: to_money(
            closes.get(ticker, 0.0) * impact.factors_on(ticker, [day])[day]
        )
        for ticker in held
    }


def _simulation_dates(
    players: list[PlayerHistoryDTO],
) -> list[tuple[int, str, list[date]]]:
    """Os dias com snapshot de cada simulação, somando os de todos os jogadores."""
    by_simulation: dict[int, tuple[str, set[date]]] = {}
    for player in players:
        _, dates = by_simulation.setdefault(
            player.simulation_id, (player.simulation_name, set())
        )
        dates.update(h.snapshot_date for h in player.history)
    return [
        (simulation_id, name, sorted(dates))
        for simulation_id, (name, dates) in by_simulation.items()
    ]


def _price_impacts() -> Callable[[int], PriceImpact]:
    """O impacto de preço de cada simulação, com a configuração salva nela."""

    @cache
    def price_impact(simulation_id: int) -> PriceImpact:
        simulation = repository.simulation.get_simulation(simulation_id)
        if simulation is None:
            return PriceImpact(simulation_id, enabled=False, k=0, decay_days=1)
        return PriceImpact(
            simulation_id,
            enabled=simulation.price_impact_enabled,
            k=simulation.price_impact_k,
            decay_days=simulation.price_impact_decay_days,
        )

    return price_impact
