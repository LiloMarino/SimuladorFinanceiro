import logging
from threading import Lock
from typing import ClassVar
from uuid import UUID

from backend.core import repository
from backend.core.dto.user import UserDTO
from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.player_colors import MAX_PLAYERS, PLAYER_COLORS, first_free_color
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.utils.lazy_dict import LazyDict

logger = logging.getLogger(__name__)

MATCH_IN_PROGRESS = "A partida já começou e você não faz parte dela. Espere a próxima."


class UserManager:
    """
    Gerenciador singleton de usuários e presença de players.

    Responsável por:
    - Controlar players ativos (autenticados e conectados) na simulação
    - Manter cache lazy de usuários por client_id para acesso rápido
    - Gerenciar lifecycle de conexão (register, unregister, auth, logout)
    - Emitir eventos de entrada/saída de players
    - Sincronizar estado com a simulação ativa
    - Dar a cada player da sala uma cor exclusiva da paleta
    """

    # 🔹 Apenas players autenticados (presença)
    _active_players: ClassVar[dict[UUID, UserDTO]] = {}

    # 🔹 Cor de cada player da sala (user_id -> chave da paleta); a sala não repete cor
    _colors: ClassVar[dict[int, str]] = {}

    # 🔹 Cores guardadas da partida salva selecionada, inclusive de quem está ausente:
    # quem participou fica travado nelas e ninguém mais toma essas cores
    _saved_colors: ClassVar[dict[int, str]] = {}

    # 🔹 Cache lazy client_id -> UserDTO (independente de presença)
    _client_user_cache: LazyDict[UUID, UserDTO | None] = LazyDict(
        loader=repository.user.get_by_client_id
    )

    _lock = Lock()

    # =========================
    # Conexão
    # =========================

    @classmethod
    def register(cls, client_id: UUID):
        logger.info(f"User connected: {client_id}")

    @classmethod
    def unregister(cls, client_id: UUID):
        logger.info(f"User disconnected: {client_id}")

        with cls._lock:
            player = cls._active_players.pop(client_id, None)
            color = cls._colors.pop(player.id, None) if player else None

        if player and color:
            cls._emit_player_exit(player, color)

    # =========================
    # Autenticação
    # =========================

    @classmethod
    def player_auth(cls, client_id: UUID) -> UserDTO | None:
        user = cls.get_user(client_id)
        if user is None:
            return None

        with cls._lock:
            if client_id in cls._active_players:
                return user

        # Com partida em andamento a cor é a da partida e só participante entra
        match_colors = cls._match_colors()

        with cls._lock:
            if client_id in cls._active_players:
                return user

            if len(cls._active_players) >= MAX_PLAYERS:
                raise ConflictError(
                    f"A sala está cheia: {MAX_PLAYERS} de {MAX_PLAYERS} jogadores."
                )

            if match_colors is not None:
                if user.id not in match_colors:
                    raise ConflictError(MATCH_IN_PROGRESS)
                color = match_colors[user.id]
            elif user.id in cls._saved_colors:
                color = cls._saved_colors[user.id]
            else:
                color = cls._free_color()

            cls._active_players[client_id] = user
            cls._colors[user.id] = color

        cls._emit_player_join(user, color)
        return user

    @classmethod
    def player_logout(cls, client_id: UUID):
        with cls._lock:
            # Remove presença ativa (se existir)
            user = cls._active_players.pop(client_id, None)
            color = cls._colors.pop(user.id, None) if user else None

        # Limpa caches da simulação (se houver simulação ativa)
        try:
            sim = SimulationManager.get_active_simulation()
            sim.clear_user_cache(client_id)
        except NoActiveSimulationError:
            pass

        # Emite evento de saída se o usuário estava ativo
        if user and color:
            cls._emit_player_exit(user, color)

        # Limpa cache lazy (força sessão a virar "guest")
        cls._client_user_cache.pop(client_id, None)

        logger.info(f"User logged out: client_id={client_id}")

    # =========================
    # Queries
    # =========================

    @classmethod
    def get_user(cls, client_id: UUID) -> UserDTO | None:
        user = cls._client_user_cache[client_id]
        if user is None:
            cls._client_user_cache.pop(client_id, None)
            return None
        return user

    @classmethod
    def get_user_id(cls, client_id: UUID) -> int:
        user = cls.get_user(client_id)
        if user is None:
            raise NotFoundError(f"Usuário não encontrado para client_id={client_id}")
        return user.id

    @classmethod
    def list_active_players(cls) -> list[UserDTO]:
        with cls._lock:
            return list(cls._active_players.values())

    # =========================
    # Cores
    # =========================

    @classmethod
    def get_color(cls, user_id: int) -> str | None:
        """Cor na sala; quem saiu no meio da partida mantém a da partida."""
        with cls._lock:
            color = cls._colors.get(user_id)
        if color is None:
            color = (cls._match_colors() or {}).get(user_id)
        return color

    @classmethod
    def room_colors(cls) -> dict[int, str]:
        """Cor de cada player da sala, por user_id."""
        with cls._lock:
            return dict(cls._colors)

    @classmethod
    def set_color(cls, client_id: UUID, color: str) -> None:
        """A cor é de quem pediu primeiro: se já tem dono, quem pediu fica com a que tinha."""
        if color not in PLAYER_COLORS:
            raise UnprocessableEntityError("Essa cor não existe na paleta.")

        if SimulationManager.has_active_simulation():
            raise ConflictError("A partida já começou: as cores ficam travadas.")

        with cls._lock:
            player = cls._active_players.get(client_id)
            if player is None:
                raise NotFoundError("Você não está na sala.")

            if player.id in cls._saved_colors:
                raise ConflictError("Sua cor é a da partida selecionada.")

            if cls._colors.get(player.id) == color:
                return

            owner = next(
                (
                    p.nickname
                    for p in cls._active_players.values()
                    if cls._colors.get(p.id) == color
                ),
                None,
            )
            if owner is not None:
                raise ConflictError(f"{owner} pegou essa cor antes.")

            if color in cls._saved_colors.values():
                raise ConflictError("Essa cor é de um jogador da partida selecionada.")

            cls._colors[player.id] = color

        cls._emit_player_color(player, color)

    @classmethod
    def apply_saved_colors(cls, colors: dict[int, str]) -> None:
        """
        Ao selecionar uma partida salva: quem já jogou volta com a cor guardada e
        fica travado; quem nunca jogou mantém a sua, se sobrou, ou ganha uma livre.
        """
        with cls._lock:
            newcomers = [p for p in cls._active_players.values() if p.id not in colors]
            if len(colors) + len(newcomers) > MAX_PLAYERS:
                raise ConflictError(
                    f"A partida tem {len(colors)} jogadores e há {len(newcomers)} "
                    f"novos na sala: passa de {MAX_PLAYERS}."
                )

            before = dict(cls._colors)
            cls._saved_colors = dict(colors)
            for player in cls._active_players.values():
                if player.id in colors:
                    cls._colors[player.id] = colors[player.id]

            # Cores guardadas valem para quem jogou; as dos ausentes ficam reservadas
            taken = set(colors.values())
            for player in newcomers:
                mine = cls._colors[player.id]
                if mine in taken:
                    mine = first_free_color(taken | set(cls._colors.values()))
                    cls._colors[player.id] = mine
                taken.add(mine)

            changed = [
                (p, cls._colors[p.id])
                for p in cls._active_players.values()
                if before.get(p.id) != cls._colors[p.id]
            ]

        for player, color in changed:
            cls._emit_player_color(player, color)

    @classmethod
    def release_saved_colors(cls) -> None:
        """Sem partida selecionada as cores da sala voltam a ser livres para trocar."""
        with cls._lock:
            cls._saved_colors = {}

    @classmethod
    def _match_colors(cls) -> dict[int, str] | None:
        """Cores dos participantes da partida em andamento; `None` sem partida."""
        if not SimulationManager.has_active_simulation():
            return None
        return repository.simulation_player.colors(
            SimulationManager.get_active_simulation_id()
        )

    @classmethod
    def _free_color(cls) -> str:
        taken = set(cls._colors.values()) | set(cls._saved_colors.values())
        try:
            return first_free_color(taken)
        except ValueError:
            raise ConflictError("A sala está cheia: não sobrou cor livre.") from None

    # =========================
    # Eventos
    # =========================

    @classmethod
    def _emit_player_join(cls, user: UserDTO, color: str):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        logger.info(f"Player joined: {user.nickname}")
        notify(
            "player_join",
            PlayerPresenceEventDTO(nickname=user.nickname, color=color).to_json(),
        )

    @classmethod
    def _emit_player_exit(cls, user: UserDTO, color: str):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        logger.info(f"Player exited: {user.nickname}")
        notify(
            "player_exit",
            PlayerPresenceEventDTO(nickname=user.nickname, color=color).to_json(),
        )

    @classmethod
    def _emit_player_color(cls, user: UserDTO, color: str):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        notify(
            "player_color",
            PlayerPresenceEventDTO(nickname=user.nickname, color=color).to_json(),
        )
