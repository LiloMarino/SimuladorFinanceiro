from backend.core import repository
from backend.core.dto.bot import RoomBotDTO
from backend.core.dto.user import UserDTO
from backend.core.runtime.user_manager import BotConfig
from backend.features.strategy.registry import STRATEGIES
from backend.features.strategy.state import derive_state


def saved_bots(simulation_id: int) -> list[tuple[UserDTO, BotConfig]]:
    """
    Os bots de uma partida salva com a estratégia em que ficaram: a ligada ou, se ela
    deu erro, a que deu. Entram na sala travados.
    """
    bots = [
        p for p in repository.simulation_player.participants(simulation_id) if p.is_bot
    ]
    if not bots:
        return []

    rows = repository.strategy.mode_rows(simulation_id)
    result: list[tuple[UserDTO, BotConfig]] = []
    for bot in bots:
        state = derive_state([r for r in rows if r.user_id == bot.id])
        key = state.key or (state.error.strategy_key if state.error else None)
        params = state.params or (state.error.params if state.error else None)
        if key in STRATEGIES:
            result.append((bot, BotConfig(key, params or {}, locked=True)))
    return result


def saved_bot_infos(simulation_id: int) -> dict[int, RoomBotDTO]:
    """O bot de cada participante que é bot, por `user_id`, como a lista da sala o mostra."""
    return {
        bot.id: RoomBotDTO(
            strategy_key=config.strategy_key,
            strategy_name=STRATEGIES[config.strategy_key].name,
            params=config.params,
            locked=True,
        )
        for bot, config in saved_bots(simulation_id)
    }
