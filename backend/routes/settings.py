from typing import Any

from fastapi import APIRouter

from backend.core import repository
from backend.core.dependencies import ClientID
from backend.core.runtime.user_manager import UserManager
from backend.routes.helpers import make_response

settings_router = APIRouter()


@settings_router.get("/api/settings")
def get_settings(client_id: ClientID):
    settings = repository.settings.get_by_user_id(UserManager.get_user_id(client_id))
    return make_response(
        True,
        "Settings loaded successfully.",
        200,
        settings,
    )


@settings_router.put("/api/settings")
def update_settings(client_id: ClientID, data: dict[str, Any]):
    if not isinstance(data, dict):
        return make_response(False, "Invalid settings payload.", 400)

    user_id = UserManager.get_user_id(client_id)

    repository.settings.update_by_user_id(user_id, data)
    settings = repository.settings.get_by_user_id(user_id)

    return make_response(
        True,
        "Settings updated successfully.",
        200,
        settings,
    )
