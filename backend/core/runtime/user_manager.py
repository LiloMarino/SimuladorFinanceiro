from threading import Lock
from typing import ClassVar

from backend.core import repository
from backend.core.dto.user import UserDTO
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.core.logger import setup_logger
from backend.core.utils.lazy_dict import LazyDict
from backend.features.realtime import notify

logger = setup_logger(__name__)


class UserManager:
    # 🔹 Apenas players autenticados (presença)
    _active_players: ClassVar[dict[str, UserDTO]] = {}

    # 🔹 Cache lazy client_id -> UserDTO (independente de presença)
    _client_user_cache: LazyDict[str, UserDTO | None] = LazyDict(
        loader=repository.user.get_by_client_id
    )

    _lock = Lock()

    # =========================
    # Conexão
    # =========================

    @classmethod
    def register(cls, client_id: str):
        logger.info(f"User connected: {client_id}")

    @classmethod
    def unregister(cls, client_id: str):
        logger.info(f"User disconnected: {client_id}")

        with cls._lock:
            player = cls._active_players.pop(client_id, None)

        if player:
            cls._emit_player_exit(player)

    # =========================
    # Autenticação
    # =========================

    @classmethod
    def player_auth(cls, client_id: str) -> UserDTO | None:
        user = cls.get_user(client_id)
        if user is None:
            return None

        with cls._lock:
            if client_id in cls._active_players:
                return user

            cls._active_players[client_id] = user

        cls._emit_player_join(user)
        return user

    # =========================
    # Queries
    # =========================

    @classmethod
    def get_user(cls, client_id: str) -> UserDTO | None:
        user = cls._client_user_cache[client_id]
        if user is None:
            cls._client_user_cache.pop(client_id, None)
            return None
        return user

    @classmethod
    def get_user_id(cls, client_id: str) -> int:
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
        logger.info(f"Player joined: {user.nickname}")
        notify("player_join", {"nickname": user.nickname})

    @classmethod
    def _emit_player_exit(cls, user: UserDTO):
        logger.info(f"Player exited: {user.nickname}")
        notify("player_exit", {"nickname": user.nickname})
