from functools import wraps

from flask import request

from backend.config.toml_settings import load_toml_settings
from backend.core.exceptions import (
    SessionNotInitializedError,
)
from backend.core.exceptions.http_exceptions import ForbiddenError, NotFoundError
from backend.core.runtime.user_manager import UserManager


def require_host(func):
    """
    Permite acesso apenas ao usuário cujo nickname
    corresponde ao host definido no config.toml.

    - Lê o client_id diretamente do cookie
    - Não depende de require_client_id
    - Ordem dos decorators não importa
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        client_id = request.cookies.get("client_id")
        if not client_id:
            raise SessionNotInitializedError()

        user = UserManager.get_user(client_id)
        if user is None:
            raise NotFoundError("Usuário não encontrado.")

        settings = load_toml_settings()
        host_nickname = settings.host.nickname

        if user.nickname != host_nickname:
            raise ForbiddenError("Apenas o host pode executar essa ação.")

        return func(*args, **kwargs)

    return wrapper
