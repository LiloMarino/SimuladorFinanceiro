from backend import config
from backend.core import repository
from backend.core.dto.bot import BotParamDTO, BotReportDTO
from backend.core.dto.strategy import StrategyLogPageDTO
from backend.core.exceptions.http_exceptions import ForbiddenError, NotFoundError
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.strategy.registry import STRATEGIES
from backend.features.strategy.state import derive_state

LOG_PAGE_LIMIT = 100


def build_bots_report(simulation_ids: list[int]) -> list[BotReportDTO]:
    """Os bots das partidas com a estratégia em que terminaram: a ligada ou a que deu erro."""
    reports = []
    for simulation_id, bot in repository.simulation_player.bots(simulation_ids):
        state = derive_state(repository.strategy.mode_rows(simulation_id, bot.id))
        key = state.key or (state.error.strategy_key if state.error else None)
        if key not in STRATEGIES:
            continue
        strategy = STRATEGIES[key]
        values = state.params or (state.error.params if state.error else None) or {}
        reports.append(
            BotReportDTO(
                simulation_id=simulation_id,
                player_nickname=bot.nickname,
                strategy_key=key,
                strategy_name=strategy.name,
                params=[
                    BotParamDTO(
                        label=spec.label, value=values[spec.key], unit=spec.unit
                    )
                    for spec in strategy.params
                    if spec.key in values
                ],
                added_by=config.toml.host.nickname,
                log_open=not _is_running(simulation_id),
            )
        )
    return reports


def bot_orders(
    simulation_id: int, nickname: str, offset: int, limit: int
) -> StrategyLogPageDTO:
    """O log de ordens do bot; fechado enquanto a partida corre."""
    bot = next(
        (
            user
            for _, user in repository.simulation_player.bots([simulation_id])
            if user.nickname == nickname
        ),
        None,
    )
    if bot is None:
        raise NotFoundError("Esse bot não jogou essa partida.")
    if _is_running(simulation_id):
        raise ForbiddenError("O log do bot abre quando a partida termina.")

    rows, total = repository.strategy.log_page(
        simulation_id, bot.id, "orders", offset, min(limit, LOG_PAGE_LIMIT)
    )
    return StrategyLogPageDTO(
        items=[
            row.model_copy(
                update={
                    "strategy_name": STRATEGIES[row.strategy_key].name
                    if row.strategy_key in STRATEGIES
                    else None
                }
            )
            for row in rows
        ],
        total=total,
    )


def _is_running(simulation_id: int) -> bool:
    return (
        SimulationManager.has_running_simulation()
        and SimulationManager.get_active_simulation_id() == simulation_id
    )
