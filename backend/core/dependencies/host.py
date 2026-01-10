from fastapi import Request

from backend.config.toml_settings import load_toml_settings
from backend.core.exceptions import SessionNotInitializedError
from backend.core.exceptions.http_exceptions import ForbiddenError, NotFoundError
from backend.core.runtime.user_manager import UserManager


def require_host_user(request: Request):
    """
    Dependency que valida se o usuário atual é o host.

    - Lê client_id do cookie
    - Valida existência do usuário
    - Valida se é o host configurado
    """
    client_id = request.cookies.get("client_id")
    if not client_id:
        raise SessionNotInitializedError()

    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")

    settings = load_toml_settings()
    if user.nickname != settings.host.nickname:
        raise ForbiddenError("Apenas o host pode executar essa ação.")

    return user
