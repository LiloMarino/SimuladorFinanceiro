from decimal import Decimal

from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.dto.statistics_report import (
    OverviewReportDTO,
    PlayerRankingDTO,
    ScoreDTO,
)
from backend.features.statistics.score import MIN_SCORE_DAYS, player_score


def build_overview(players: list[PlayerHistoryDTO]) -> OverviewReportDTO:
    """
    Ranqueia os jogadores pela nota geral; quem ainda não tem nota vem depois, e o
    retorno percentual sobre o capital aportado (saldo inicial + aportes) desempata.
    """
    performances = sorted(
        (_performance(player) for player in players),
        key=lambda p: _ranking_key(p[4], p[1]),
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
        )
        for position, (
            player,
            return_percent,
            networth,
            return_value,
            score,
        ) in enumerate(performances, start=1)
    ]

    average_return = (
        sum((p.return_percent for p in ranked), Decimal(0)) / len(ranked)
        if ranked
        else None
    )
    return OverviewReportDTO(
        players=ranked, average_return=average_return, min_score_days=MIN_SCORE_DAYS
    )


def capital_provided(player: PlayerHistoryDTO) -> Decimal:
    return player.starting_cash + player.history[-1].total_contribution


def _ranking_key(score: ScoreDTO | None, return_percent: Decimal):
    return (score is not None, score.total if score else Decimal(0), return_percent)


def _performance(
    player: PlayerHistoryDTO,
) -> tuple[PlayerHistoryDTO, Decimal, Decimal, Decimal, ScoreDTO | None]:
    last = player.history[-1]
    capital = capital_provided(player)
    return_value = last.total_networth - capital
    return_percent = return_value / capital if capital > 0 else Decimal(0)
    score = player_score(player.history)
    return player, return_percent, last.total_networth, return_value, score
