from fastapi import APIRouter
from fastapi.responses import JSONResponse
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


@settings_router.get("")
def get_settings(client_id: ClientID):
    settings = repository.settings.get_by_user_id(UserManager.get_user_id(client_id))
    return JSONResponse(content={"data": settings})


@settings_router.put("")
def update_settings(client_id: ClientID, data: SettingsRequest):
    user_id = UserManager.get_user_id(client_id)

    repository.settings.update_by_user_id(user_id, data.model_dump())
    settings = repository.settings.get_by_user_id(user_id)

    return JSONResponse(content={"data": settings})
