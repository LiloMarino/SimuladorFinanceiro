from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from backend.core import repository
from backend.core.dependencies import ClientID
from backend.core.runtime.user_manager import UserManager

settings_router = APIRouter(prefix="/api/settings", tags=["Settings"])


class OrderNotificationSettings(BaseModel):
    executed: bool
    partial: bool


class SettingsRequest(BaseModel):
    orders: OrderNotificationSettings

    model_config = ConfigDict(extra="allow")


DEFAULT_SETTINGS = SettingsRequest(
    orders=OrderNotificationSettings(
        executed=True,
        partial=True,
    )
)


@settings_router.get(
    "",
    response_model=SettingsRequest,
    summary="Obter configurações do usuário",
    description="Retorna as configurações pessoais do usuário (notificações de ordens, etc.).",
)
def get_settings(client_id: ClientID):
    """
    Retorna as configurações do usuário.
    """
    settings = repository.settings.get_by_user_id(UserManager.get_user_id(client_id))
    return SettingsRequest.model_validate(
        {
            **DEFAULT_SETTINGS.model_dump(),
            **settings,
        }
    )


@settings_router.put(
    "",
    response_model=SettingsRequest,
    summary="Atualizar configurações do usuário",
    description="Atualiza as configurações pessoais do usuário.",
)
def update_settings(client_id: ClientID, data: SettingsRequest):
    """
    Atualiza as configurações do usuário.
    """
    user_id = UserManager.get_user_id(client_id)

    repository.settings.update_by_user_id(user_id, data.model_dump())
    settings = repository.settings.get_by_user_id(user_id)

    return SettingsRequest.model_validate(settings)
