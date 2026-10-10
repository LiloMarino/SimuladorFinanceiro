from decimal import Decimal

from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.dto.statistics_report import OverviewReportDTO, PlayerRankingDTO


def build_overview(players: list[PlayerHistoryDTO]) -> OverviewReportDTO:
    """
    Ranqueia os jogadores pelo retorno percentual sobre o capital aportado
    (saldo inicial + aportes mensais até o último snapshot).
    """
    performances = sorted(
        (_performance(player) for player in players),
        key=lambda p: p[1],
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
        )
        for position, (player, return_percent, networth, return_value) in enumerate(
            performances, start=1
        )
    ]

    average_return = (
        sum((p.return_percent for p in ranked), Decimal(0)) / len(ranked)
        if ranked
        else None
    )
    return OverviewReportDTO(players=ranked, average_return=average_return)


def capital_provided(player: PlayerHistoryDTO) -> Decimal:
    return player.starting_cash + player.history[-1].total_contribution


def _performance(
    player: PlayerHistoryDTO,
) -> tuple[PlayerHistoryDTO, Decimal, Decimal, Decimal]:
    last = player.history[-1]
    capital = capital_provided(player)
    return_value = last.total_networth - capital
    return_percent = return_value / capital if capital > 0 else Decimal(0)
    return player, return_percent, last.total_networth, return_value
