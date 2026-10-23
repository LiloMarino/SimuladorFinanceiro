from __future__ import annotations

from datetime import date

from backend.core import repository
from backend.core.dto.strategy import StrategyLastOrderDTO, StrategyPanelDTO
from backend.core.enum import StrategyOrderStatus
from backend.features.statistics.returns import cumulative_returns, ibov_cumulative
from backend.features.statistics.risk import daily_returns


def build_panel(simulation_id: int, user_id: int, since: date) -> StrategyPanelDTO:
    """O que a estratégia fez desde `since`: ordens por situação, retorno e Ibovespa."""
    counts = repository.strategy.order_counts(simulation_id, user_id, since)

    # O retorno parte do patrimônio do dia em que ligou e descarta os aportes
    history = [
        point
        for point in repository.portfolio.get_patrimonial_history(user_id)
        if point.snapshot_date >= since
    ]
    returns = cumulative_returns(history, daily_returns(history))
    ibov = ibov_cumulative([point.snapshot_date for point in history])

    last = repository.strategy.last_order(simulation_id, user_id)
    return StrategyPanelDTO(
        orders_total=sum(counts.values()),
        executed=counts.get(StrategyOrderStatus.EXECUTED, 0),
        partial=counts.get(StrategyOrderStatus.PARTIAL, 0),
        open=counts.get(StrategyOrderStatus.OPEN, 0),
        canceled=counts.get(StrategyOrderStatus.CANCELED, 0),
        refused=counts.get(StrategyOrderStatus.REFUSED, 0),
        return_pct=returns[-1][1] if len(returns) > 1 else None,
        ibov_pct=ibov[-1][1] if len(ibov) > 1 else None,
        last_order=StrategyLastOrderDTO(
            action=last.action,
            ticker=last.ticker,
            asset_name=last.asset_name,
            quantity=last.quantity,
            order_date=last.event_date,
            order_type=last.order_type,
        )
        if last and last.action
        else None,
    )
