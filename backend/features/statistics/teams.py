"""
Agregação por equipe: o valor da equipe é a média simples dos membros, em toda
métrica. Quem ainda não tem o valor (nota antes de 63 pregões, Sharpe sem oscilação)
fica fora da média daquela métrica, e a equipe de uma pessoa vale o valor dela.
Volume, IR e negócios são totais, não desempenho: esses somam.
"""

from collections import defaultdict
from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from backend.core.dto.statistics_report import (
    MonthlyVolumeDTO,
    PlayerCompositionDTO,
    PlayerOperationsDTO,
    PlayerReturnsDTO,
    PlayerRiskDTO,
    PlayerScoreHistoryDTO,
    SeriesPointDTO,
    TeamCompositionDTO,
    TeamOperationsDTO,
    TeamReturnsDTO,
    TeamRiskDTO,
    TeamScoreHistoryDTO,
)


def mean(values: Iterable[Decimal | int | None]) -> Decimal | None:
    """Média dos valores medidos; `None` quando nenhum membro tem o valor."""
    measured = [Decimal(v) for v in values if v is not None]
    return sum(measured, Decimal(0)) / len(measured) if measured else None


def total(values: Iterable[Decimal | int]) -> Decimal:
    return sum((Decimal(v) for v in values), Decimal(0))


def group_by_team[
    T: (
        PlayerReturnsDTO,
        PlayerRiskDTO,
        PlayerCompositionDTO,
        PlayerOperationsDTO,
        PlayerScoreHistoryDTO,
    )
](
    players: list[T],
) -> dict[int, list[T]]:
    """Os jogadores de cada equipe, na ordem do índice da equipe."""
    groups: dict[int, list[T]] = defaultdict(list)
    for player in players:
        if player.team is not None:
            groups[player.team].append(player)
    return dict(sorted(groups.items()))


def mean_series(series: list[list[SeriesPointDTO]]) -> list[SeriesPointDTO]:
    """Em cada dia, a média dos membros que têm ponto nele (quem entrou depois começa mais tarde)."""
    by_day: dict[date, list[Decimal]] = defaultdict(list)
    for member in series:
        for point in member:
            by_day[point.date].append(point.value)
    return [
        SeriesPointDTO(date=day, value=sum(values, Decimal(0)) / len(values))
        for day, values in sorted(by_day.items())
    ]


def team_returns(players: list[PlayerReturnsDTO]) -> list[TeamReturnsDTO]:
    return [
        TeamReturnsDTO(
            team=team,
            simulation_id=members[0].simulation_id,
            members=len(members),
            networth=mean_series([m.networth for m in members]),
            cumulative_return=mean_series([m.cumulative_return for m in members]),
            capital_provided=mean([m.capital_provided for m in members]) or Decimal(0),
            annual_return=mean(m.annual_return for m in members),
            months_above_cdi=mean(m.months_above_cdi for m in members) or Decimal(0),
            positive_months=mean(m.positive_months for m in members) or Decimal(0),
            months=max(m.months for m in members),
        )
        for team, members in group_by_team(players).items()
    ]


def team_score_history(
    players: list[PlayerScoreHistoryDTO],
) -> list[TeamScoreHistoryDTO]:
    return [
        TeamScoreHistoryDTO(
            team=team,
            simulation_id=members[0].simulation_id,
            points=mean_series([m.points for m in members]),
        )
        for team, members in group_by_team(players).items()
    ]


def team_risk(players: list[PlayerRiskDTO]) -> list[TeamRiskDTO]:
    return [
        TeamRiskDTO(
            team=team,
            simulation_id=members[0].simulation_id,
            members=len(members),
            max_drawdown=mean(m.max_drawdown for m in members),
            annual_volatility=mean(m.annual_volatility for m in members),
            sharpe_ratio=mean(m.sharpe_ratio for m in members),
            sortino_ratio=mean(m.sortino_ratio for m in members),
            time_underwater=mean(m.time_underwater for m in members),
            worst_month=mean(m.worst_month for m in members),
            annual_return=mean(m.annual_return for m in members),
        )
        for team, members in group_by_team(players).items()
    ]


def _shares(player: PlayerCompositionDTO) -> tuple[Decimal, Decimal, Decimal] | None:
    """Fração de caixa, renda variável e renda fixa no último dia."""
    if not player.history:
        return None
    last = player.history[-1]
    if last.total_networth <= 0:
        return None
    return (
        last.total_cash / last.total_networth,
        last.total_equity / last.total_networth,
        last.total_fixed / last.total_networth,
    )


def team_composition(players: list[PlayerCompositionDTO]) -> list[TeamCompositionDTO]:
    result = []
    for team, members in group_by_team(players).items():
        shares = [s for s in map(_shares, members) if s is not None]
        result.append(
            TeamCompositionDTO(
                team=team,
                simulation_id=members[0].simulation_id,
                members=len(members),
                cash_share=mean(s[0] for s in shares),
                equity_share=mean(s[1] for s in shares),
                fixed_share=mean(s[2] for s in shares),
            )
        )
    return result


def _sum_monthly(series: list[list[MonthlyVolumeDTO]]) -> list[MonthlyVolumeDTO]:
    by_month: dict[date, list[MonthlyVolumeDTO]] = defaultdict(list)
    for member in series:
        for month in member:
            by_month[month.month].append(month)
    return [
        MonthlyVolumeDTO(
            month=month,
            bought=total(m.bought for m in items),
            sold=total(m.sold for m in items),
            buy_count=sum(m.buy_count for m in items),
            sell_count=sum(m.sell_count for m in items),
        )
        for month, items in sorted(by_month.items())
    ]


def _impact_cost(members: list[PlayerOperationsDTO]) -> Decimal | None:
    """Soma do custo de impacto de quem o mede; `None` com o impacto de preço desligado."""
    costs = [m.impact_cost for m in members if m.impact_cost is not None]
    return total(costs) if costs else None


def team_operations(players: list[PlayerOperationsDTO]) -> list[TeamOperationsDTO]:
    return [
        TeamOperationsDTO(
            team=team,
            simulation_id=members[0].simulation_id,
            members=len(members),
            buy_trades=sum(m.buy_trades for m in members),
            sell_trades=sum(m.sell_trades for m in members),
            traded_volume=total(m.traded_volume for m in members),
            income_tax_paid=total(m.income_tax_paid for m in members),
            turnover=mean(m.turnover for m in members),
            impact_cost=_impact_cost(members),
            monthly_volume=_sum_monthly([m.monthly_volume for m in members]),
        )
        for team, members in group_by_team(players).items()
    ]
