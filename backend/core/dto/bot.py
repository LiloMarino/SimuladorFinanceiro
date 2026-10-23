from backend.core.dto.base import BaseDTO
from backend.core.dto.strategy import StrategyParamValue


class RoomBotDTO(BaseDTO):
    """O bot na lista da sala: a estratégia que ele joga e se a partida salva o trava."""

    strategy_key: str
    strategy_name: str
    params: dict[str, StrategyParamValue]
    # Bot da partida salva selecionada: não se configura nem se remove
    locked: bool


class BotParamDTO(BaseDTO):
    label: str
    value: StrategyParamValue
    # "dias", "%"...; nulo quando o valor não tem unidade
    unit: str | None


class BotReportDTO(BaseDTO):
    """O bot de uma partida como o ranking o mostra: o que ele joga e quem o pôs na sala."""

    simulation_id: int
    player_nickname: str
    strategy_key: str
    strategy_name: str
    # Um parâmetro por linha, com o rótulo e a unidade da estratégia
    params: list[BotParamDTO]
    # Apelido do host da sala, que adicionou o bot
    added_by: str
    # O log das ordens abre quando a partida termina: antes, mostraria a jogada ao vivo
    log_open: bool
