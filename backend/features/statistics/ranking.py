from decimal import Decimal

from backend.core.dto.player_history import (
    PerformanceReportDTO,
    PlayerHistoryDTO,
    PlayerPerformanceDTO,
)
from backend.features.statistics.risk import build_risk_metrics


def build_performance_report(players: list[PlayerHistoryDTO]) -> PerformanceReportDTO:
    """
    Ranqueia os jogadores pelo retorno percentual sobre o capital aportado
    (saldo inicial + aportes mensais até o último snapshot).
    """
    performances = [_performance(player) for player in players]
    performances.sort(key=lambda p: p[1], reverse=True)

    ranked = [
        PlayerPerformanceDTO(
            **player.model_dump(),
            position=position,
            total_networth=networth,
            return_value=return_value,
            return_percent=return_percent,
            risk=build_risk_metrics(player.history),
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

    return PerformanceReportDTO(players=ranked, average_return=average_return)


def _performance(
    player: PlayerHistoryDTO,
) -> tuple[PlayerHistoryDTO, Decimal, Decimal, Decimal]:
    last = player.history[-1]
    capital = player.starting_cash + last.total_contribution
    return_value = last.total_networth - capital
    return_percent = return_value / capital if capital > 0 else Decimal(0)
    return player, return_percent, last.total_networth, return_value
