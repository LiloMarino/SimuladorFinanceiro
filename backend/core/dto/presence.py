from backend.core.dto.base import BaseDTO
from backend.core.dto.bot import RoomBotDTO
from backend.core.enum import PlayerActivity, Profession


class PlayerPresenceEventDTO(BaseDTO):
    """Entrada, saída e troca de cor, equipe ou atividade de um jogador: a cor é a chave da paleta."""

    nickname: str
    color: str
    # Índice da equipe (1 a 10); nulo fora do modo em equipes ou enquanto não escolheu
    team: int | None = None
    # Profissão no viver de renda com profissões; nula nos outros modos
    profession: Profession | None = None
    # O que o jogador está fazendo; nulo é "Online" (partida em andamento ou sem aviso ainda)
    activity: PlayerActivity | None = None
    # Presente quando o jogador é um bot da sala: a estratégia que ele joga
    bot: RoomBotDTO | None = None
    # Só no evento de configurar o bot, que pode renomeá-lo: o nome de antes
    previous_nickname: str | None = None


class PlayerRemovedEventDTO(BaseDTO):
    """Só para quem o host tirou da sala: a página encerra a sessão e conta o motivo."""

    nickname: str
