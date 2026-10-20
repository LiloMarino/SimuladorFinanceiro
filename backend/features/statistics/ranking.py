from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.dto.statistics_report import (
    OverviewReportDTO,
    PlayerRankingDTO,
    ScoreAxis,
    ScoreAxisDTO,
    ScoreDTO,
    ScoreMetricDTO,
    TeamPullerDTO,
    TeamRankingDTO,
)
from backend.core.enum import PlayerGrouping, TeamNaming, VictoryCriterion
from backend.features.statistics import risk
from backend.features.statistics.score import MIN_SCORE_DAYS, player_score
from backend.features.statistics.teams import mean


def build_overview(
    players: list[PlayerHistoryDTO],
    criterion: VictoryCriterion = VictoryCriterion.SCORE,
    *,
    in_teams: bool = False,
    team_naming: TeamNaming = TeamNaming.COLOR,
) -> OverviewReportDTO:
    """
    Ranqueia os jogadores pelo critério de vitória; quem ainda não tem o valor
    (nota antes de 63 pregões, Sharpe sem oscilação) vem depois, e o retorno
    percentual sobre o capital aportado (saldo inicial + aportes) desempata.

    Em equipes, o valor da equipe em cada critério é a média dos membros e a
    equipe com a melhor média vence; o patrimônio médio desempata.
    """
    performances = sorted(
        (_performance(player) for player in players),
        key=lambda p: _ranking_key(criterion, p),
        reverse=True,
    )

    teams = _rank_teams(performances, criterion) if in_teams else []
    contributions = {
        (member.simulation_id, member.player_nickname): contribution
        for team in teams
        for member, contribution in team.contributions
    }

    leader_value = (
        _criterion_value(criterion, performances[0]) if performances else None
    )
    ranked = [
        PlayerRankingDTO(
            player_nickname=player.player_nickname,
            color=player.color,
            simulation_id=player.simulation_id,
            simulation_name=player.simulation_name,
            team=player.team,
            position=position,
            total_networth=networth,
            return_value=return_value,
            return_percent=return_percent,
            days=len(player.history),
            months=len(risk.monthly_returns(risk.daily_returns(player.history))),
            score=score,
            sharpe_ratio=sharpe,
            criterion_value=_criterion_value(criterion, performance),
            leader_gap=_gap(leader_value, _criterion_value(criterion, performance)),
            weakest_axis=_weakest_axis(score),
            team_contribution=contributions.get(
                (player.simulation_id, player.player_nickname)
            ),
        )
        for position, performance in enumerate(performances, start=1)
        for (
            player,
            return_percent,
            networth,
            return_value,
            score,
            sharpe,
        ) in [performance]
    ]

    average_return = (
        sum((p.return_percent for p in ranked), Decimal(0)) / len(ranked)
        if ranked
        else None
    )
    return OverviewReportDTO(
        player_grouping=PlayerGrouping.TEAMS if in_teams else PlayerGrouping.INDIVIDUAL,
        team_naming=team_naming,
        players=ranked,
        teams=[team.dto for team in teams],
        average_return=average_return,
        min_score_days=MIN_SCORE_DAYS,
        criterion=criterion,
    )


def capital_provided(player: PlayerHistoryDTO) -> Decimal:
    return player.starting_cash + player.history[-1].total_contribution


type Performance = tuple[
    PlayerHistoryDTO, Decimal, Decimal, Decimal, ScoreDTO | None, Decimal | None
]


@dataclass(frozen=True)
class _RankedTeam:
    """Equipe já ranqueada, com a contribuição de cada membro para a média dela."""

    dto: TeamRankingDTO
    contributions: list[tuple[PlayerHistoryDTO, Decimal | None]]


def _rank_teams(
    performances: list[Performance], criterion: VictoryCriterion
) -> list[_RankedTeam]:
    groups: dict[int, list[Performance]] = defaultdict(list)
    for performance in performances:
        if performance[0].team is not None:
            groups[performance[0].team].append(performance)

    aggregates = [
        (team, members, _team_value(criterion, members), _team_networth(members))
        for team, members in groups.items()
    ]
    aggregates.sort(
        key=lambda a: (a[2] is not None, a[2] or Decimal(0), a[3]), reverse=True
    )
    leader_value = aggregates[0][2] if aggregates else None

    ranked = []
    for position, (team, members, value, networth) in enumerate(aggregates, start=1):
        score = _team_score(members)
        contributions = [
            (member, _contribution(criterion, member, value)) for member in members
        ]
        ranked.append(
            _RankedTeam(
                TeamRankingDTO(
                    team=team,
                    simulation_id=members[0][0].simulation_id,
                    position=position,
                    members=len(members),
                    measured_members=sum(
                        1 for m in members if _criterion_value(criterion, m) is not None
                    ),
                    total_networth=networth,
                    return_value=mean(m[3] for m in members) or Decimal(0),
                    return_percent=mean(m[1] for m in members) or Decimal(0),
                    score=score,
                    sharpe_ratio=mean(m[5] for m in members),
                    criterion_value=value,
                    leader_gap=_gap(leader_value, value),
                    weakest_axis=_weakest_axis(score),
                    top_puller=_top_puller(criterion, contributions, score),
                ),
                [(member[0], c) for member, c in contributions],
            )
        )
    return ranked


def _team_value(
    criterion: VictoryCriterion, members: list[Performance]
) -> Decimal | None:
    return mean(_criterion_value(criterion, m) for m in members)


def _team_networth(members: list[Performance]) -> Decimal:
    return mean(m[2] for m in members) or Decimal(0)


def _team_score(members: list[Performance]) -> ScoreDTO | None:
    """Nota da equipe: cada eixo (e cada métrica) é a média dos membros que o medem."""
    scores = [m[4] for m in members if m[4] is not None]
    if not scores:
        return None
    axes = []
    for index, template in enumerate(scores[0].axes):
        metrics = [
            ScoreMetricDTO(
                metric=metric.metric,
                value=mean(s.axes[index].metrics[i].value for s in scores),
                points=mean(s.axes[index].metrics[i].points for s in scores),
            )
            for i, metric in enumerate(template.metrics)
        ]
        axes.append(
            ScoreAxisDTO(
                axis=template.axis,
                points=mean(s.axes[index].points for s in scores),
                metrics=metrics,
            )
        )
    return ScoreDTO(total=mean(s.total for s in scores) or Decimal(0), axes=axes)


def _contribution(
    criterion: VictoryCriterion, member: Performance, team_value: Decimal | None
) -> Decimal | None:
    """Quanto o membro passa (ou fica abaixo) da média da equipe no critério."""
    value = _criterion_value(criterion, member)
    return value - team_value if value is not None and team_value is not None else None


def _top_puller(
    criterion: VictoryCriterion,
    contributions: list[tuple[Performance, Decimal | None]],
    team_score: ScoreDTO | None,
) -> TeamPullerDTO | None:
    """Quem mais puxou a média para cima; equipe de uma pessoa não tem puxador."""
    if len(contributions) < 2:
        return None
    pulling = [(m, c) for m, c in contributions if c is not None and c > 0]
    if not pulling:
        return None
    member, contribution = max(pulling, key=lambda item: item[1] or Decimal(0))
    player = member[0]
    axis, axis_gap = (
        _strongest_axis(member[4], team_score)
        if criterion is VictoryCriterion.SCORE
        else (None, None)
    )
    return TeamPullerDTO(
        player_nickname=player.player_nickname,
        color=player.color,
        contribution=contribution or Decimal(0),
        axis=axis,
        axis_gap=axis_gap,
    )


def _strongest_axis(
    member: ScoreDTO | None, team: ScoreDTO | None
) -> tuple[ScoreAxis | None, Decimal | None]:
    """O eixo em que o membro mais passa da média da equipe."""
    if member is None or team is None:
        return None, None
    gaps: list[tuple[ScoreAxis, Decimal]] = [
        (m.axis, m.points - t.points)
        for m, t in zip(member.axes, team.axes, strict=True)
        if m.points is not None and t.points is not None
    ]
    if not gaps:
        return None, None
    return max(gaps, key=lambda item: item[1])


def _criterion_value(
    criterion: VictoryCriterion, performance: Performance
) -> Decimal | None:
    _, return_percent, networth, _, score, sharpe = performance
    return {
        VictoryCriterion.SCORE: score.total if score else None,
        VictoryCriterion.RETURN: return_percent,
        VictoryCriterion.NETWORTH: networth,
        VictoryCriterion.SHARPE: sharpe,
    }[criterion]


def _gap(leader: Decimal | None, value: Decimal | None) -> Decimal | None:
    return leader - value if leader is not None and value is not None else None


def _weakest_axis(score: ScoreDTO | None) -> ScoreAxis | None:
    measured = [a for a in score.axes if a.points is not None] if score else []
    return (
        min(measured, key=lambda a: a.points or Decimal(0)).axis if measured else None
    )


def _ranking_key(criterion: VictoryCriterion, performance: Performance):
    value = _criterion_value(criterion, performance)
    return (value is not None, value or Decimal(0), performance[1])


def _performance(player: PlayerHistoryDTO) -> Performance:
    last = player.history[-1]
    capital = capital_provided(player)
    return_value = last.total_networth - capital
    return_percent = return_value / capital if capital > 0 else Decimal(0)
    days = risk.daily_returns(player.history)
    sharpe = risk.sharpe_ratio(days, risk.annual_volatility([r for _, r in days]))
    score = player_score(player.history)
    return player, return_percent, last.total_networth, return_value, score, sharpe
