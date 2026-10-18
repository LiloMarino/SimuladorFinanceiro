from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from backend import config
from backend.core import repository
from backend.core.dependencies import ClientID
from backend.core.runtime.user_manager import UserManager

settings_router = APIRouter(prefix="/api/settings", tags=["Settings"])


class OrderNotificationSettings(BaseModel):
    executed: bool
    partial: bool


class PlayerNotificationSettings(BaseModel):
    join_exit: bool


class SettingsRequest(BaseModel):
    orders: OrderNotificationSettings
    players: PlayerNotificationSettings

    model_config = ConfigDict(extra="allow")


class SettingsResponse(SettingsRequest):
    """As preferências do usuário mais o modo debug do servidor, só leitura."""

    debug: bool


DEFAULT_SETTINGS = SettingsRequest(
    orders=OrderNotificationSettings(
        executed=True,
        partial=True,
    ),
    players=PlayerNotificationSettings(join_exit=True),
)


def _with_debug(settings: dict) -> SettingsResponse:
    """Sobrepõe o `debug` do config.toml, mesmo que o banco tenha um valor antigo."""
    return SettingsResponse.model_validate(
        {**settings, "debug": config.toml.debug.enabled}
    )


@settings_router.get(
    "",
    response_model=SettingsResponse,
    summary="Obter configurações do usuário",
    description=(
        "Retorna as configurações pessoais do usuário (notificações de ordens, etc.) "
        "e se o servidor está em modo debug, definido no boot (`--debug` ou config.toml)."
    ),
)
def get_settings(client_id: ClientID):
    """
    Retorna as configurações do usuário.
    """
    settings = repository.settings.get_by_user_id(UserManager.get_user_id(client_id))
    return _with_debug(
        {
            **DEFAULT_SETTINGS.model_dump(),
            **settings,
        }
    )


@settings_router.put(
    "",
    response_model=SettingsResponse,
    summary="Atualizar configurações do usuário",
    description="Atualiza as configurações pessoais do usuário.",
)
def update_settings(client_id: ClientID, data: SettingsRequest):
    """
    Atualiza as configurações do usuário.
    """
    user_id = UserManager.get_user_id(client_id)

    # O debug é do servidor: o cliente não o grava (`extra="allow"` deixaria passar)
    repository.settings.update_by_user_id(user_id, data.model_dump(exclude={"debug"}))
    settings = repository.settings.get_by_user_id(user_id)

    return _with_debug(settings)
