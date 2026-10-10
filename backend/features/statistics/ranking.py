from decimal import Decimal

from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.dto.statistics_report import (
    OverviewReportDTO,
    PlayerRankingDTO,
    ScoreDTO,
)
from backend.core.enum import VictoryCriterion
from backend.features.statistics import risk
from backend.features.statistics.score import MIN_SCORE_DAYS, player_score


def build_overview(
    players: list[PlayerHistoryDTO],
    criterion: VictoryCriterion = VictoryCriterion.SCORE,
) -> OverviewReportDTO:
    """
    Ranqueia os jogadores pelo critério de vitória; quem ainda não tem o valor
    (nota antes de 63 pregões, Sharpe sem oscilação) vem depois, e o retorno
    percentual sobre o capital aportado (saldo inicial + aportes) desempata.
    """
    performances = sorted(
        (_performance(player) for player in players),
        key=lambda p: _ranking_key(criterion, p),
        reverse=True,
    )

    ranked = [
        PlayerRankingDTO(
            player_nickname=player.player_nickname,
            simulation_id=player.simulation_id,
            simulation_name=player.simulation_name,
            position=position,
            total_networth=networth,
            return_value=return_value,
            return_percent=return_percent,
            days=len(player.history),
            score=score,
            sharpe_ratio=sharpe,
        )
        for position, (
            player,
            return_percent,
            networth,
            return_value,
            score,
            sharpe,
        ) in enumerate(performances, start=1)
    ]

    average_return = (
        sum((p.return_percent for p in ranked), Decimal(0)) / len(ranked)
        if ranked
        else None
    )
    return OverviewReportDTO(
        players=ranked,
        average_return=average_return,
        min_score_days=MIN_SCORE_DAYS,
        criterion=criterion,
    )


def capital_provided(player: PlayerHistoryDTO) -> Decimal:
    return player.starting_cash + player.history[-1].total_contribution


type Performance = tuple[
    PlayerHistoryDTO, Decimal, Decimal, Decimal, ScoreDTO | None, Decimal | None
]


def _ranking_key(criterion: VictoryCriterion, performance: Performance):
    _, return_percent, networth, _, score, sharpe = performance
    value = {
        VictoryCriterion.SCORE: score.total if score else None,
        VictoryCriterion.RETURN: return_percent,
        VictoryCriterion.NETWORTH: networth,
        VictoryCriterion.SHARPE: sharpe,
    }[criterion]
    return (value is not None, value or Decimal(0), return_percent)


def _performance(player: PlayerHistoryDTO) -> Performance:
    last = player.history[-1]
    capital = capital_provided(player)
    return_value = last.total_networth - capital
    return_percent = return_value / capital if capital > 0 else Decimal(0)
    days = risk.daily_returns(player.history)
    sharpe = risk.sharpe_ratio(days, risk.annual_volatility([r for _, r in days]))
    score = player_score(player.history)
    return player, return_percent, last.total_networth, return_value, score, sharpe
