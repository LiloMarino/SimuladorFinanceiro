import logging
from threading import Lock
from typing import ClassVar
from uuid import UUID

from backend.core import repository
from backend.core.dto.user import UserDTO
from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.core.utils.lazy_dict import LazyDict

logger = logging.getLogger(__name__)


class UserManager:
    """
    Gerenciador singleton de usuários e presença de players.

    Responsável por:
    - Controlar players ativos (autenticados e conectados) na simulação
    - Manter cache lazy de usuários por client_id para acesso rápido
    - Gerenciar lifecycle de conexão (register, unregister, auth, logout)
    - Emitir eventos de entrada/saída de players
    - Sincronizar estado com a simulação ativa
    """

    # 🔹 Apenas players autenticados (presença)
    _active_players: ClassVar[dict[UUID, UserDTO]] = {}

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

        if player:
            cls._emit_player_exit(player)

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

            cls._active_players[client_id] = user

        cls._emit_player_join(user)
        return user

    @classmethod
    def player_logout(cls, client_id: UUID):
        from backend.core.runtime.simulation_manager import (  # noqa: PLC0415
            SimulationManager,
        )

        with cls._lock:
            # Remove presença ativa (se existir)
            user = cls._active_players.pop(client_id, None)

        # Limpa caches da simulação (se houver simulação ativa)
        try:
            sim = SimulationManager.get_active_simulation()
            sim.clear_user_cache(client_id)
        except NoActiveSimulationError:
            pass

        # Emite evento de saída se o usuário estava ativo
        if user:
            cls._emit_player_exit(user)

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
    # Eventos
    # =========================

    @classmethod
    def _emit_player_join(cls, user: UserDTO):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        logger.info(f"Player joined: {user.nickname}")
        notify("player_join", PlayerPresenceEventDTO(nickname=user.nickname).to_json())

    @classmethod
    def _emit_player_exit(cls, user: UserDTO):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        logger.info(f"Player exited: {user.nickname}")
        notify("player_exit", PlayerPresenceEventDTO(nickname=user.nickname).to_json())
