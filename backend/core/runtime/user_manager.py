from threading import Lock
from typing import ClassVar

from backend.core import repository
from backend.core.dto.user import UserDTO
from backend.core.logger import setup_logger
from backend.core.utils.lazy_dict import LazyDict

logger = setup_logger(__name__)


class UserManager:
    _active_users: ClassVar[set[str]] = set()
    _user_id_map: LazyDict[str, UserDTO | None] = LazyDict(
        loader=repository.user.get_by_client_id
    )
    _lock = Lock()

    @classmethod
    def register(cls, client_id: str):
        logger.info(f"User connected: {client_id}")
        with cls._lock:
            cls._active_users.add(client_id)

    @classmethod
    def unregister(cls, client_id: str):
        logger.info(f"User disconnected: {client_id}")
        with cls._lock:
            cls._active_users.discard(client_id)

    @classmethod
    def get_user_id(cls, client_id: str) -> int:
        user = cls._user_id_map[client_id]
        if user is None:
            raise RuntimeError(f"User não encontrado para client_id={client_id}")
        return user.id

    @classmethod
    def list_active_users(cls):
        with cls._lock:
            return list(cls._active_users)

    @classmethod
    def is_active(cls, client_id: str):
        with cls._lock:
            return client_id in cls._active_users
