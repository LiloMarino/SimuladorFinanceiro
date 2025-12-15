import typing
from threading import Lock

from backend.core.logger import setup_logger

logger = setup_logger(__name__)


class UserManager:
    _active_users: typing.ClassVar[set[str]] = set()
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
    def list_active_users(cls):
        with cls._lock:
            return list(cls._active_users)

    @classmethod
    def is_active(cls, client_id: str):
        with cls._lock:
            return client_id in cls._active_users
