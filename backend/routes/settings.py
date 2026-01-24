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


@settings_router.get("", response_model=SettingsRequest)
def get_settings(client_id: ClientID):
    settings = repository.settings.get_by_user_id(UserManager.get_user_id(client_id))
    return SettingsRequest.model_validate(settings)


@settings_router.put("", response_model=SettingsRequest)
def update_settings(client_id: ClientID, data: SettingsRequest):
    user_id = UserManager.get_user_id(client_id)

    repository.settings.update_by_user_id(user_id, data.model_dump())
    settings = repository.settings.get_by_user_id(user_id)

    return SettingsRequest.model_validate(settings)
