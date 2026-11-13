from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import APIKeyCookie

from backend import config
from backend.core.dto.user import UserDTO
from backend.core.exceptions import SessionNotInitializedError
from backend.core.exceptions.http_exceptions import ForbiddenError, NotFoundError
from backend.core.runtime.user_manager import UserManager

client_id_cookie = APIKeyCookie(
    name="client_id",
    auto_error=False,
)


def get_client_id(
    client_id: Annotated[str | None, Depends(client_id_cookie)],
) -> UUID:
    if not client_id:
        raise SessionNotInitializedError()
    return UUID(client_id)


def get_current_user(
    client_id: Annotated[UUID, Depends(get_client_id)],
):
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    return user


def verify_host(
    user: Annotated[UserDTO, Depends(get_current_user)],
) -> None:
    if user.nickname != config.toml.host.nickname:
        raise ForbiddenError("Apenas o host pode executar essa ação.")
