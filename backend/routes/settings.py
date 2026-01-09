from fastapi import APIRouter, status
from pydantic import BaseModel

from backend.core import repository
from backend.core.runtime.user_manager import UserManager
from backend.fastapi_deps import ClientID
from backend.fastapi_helpers import make_response

settings_router = APIRouter(prefix="/api", tags=["settings"])


@settings_router.get("/settings")
def get_settings(client_id: ClientID):
    settings = repository.settings.get_by_user_id(UserManager.get_user_id(client_id))
    return make_response(
        True,
        "Settings loaded successfully.",
        status_code=status.HTTP_200_OK,
        data=settings,
    )


@settings_router.put("/settings")
def update_settings(client_id: ClientID, data: dict):
    if not isinstance(data, dict):
        return make_response(
            False,
            "Invalid settings payload.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user_id = UserManager.get_user_id(client_id)

    repository.settings.update_by_user_id(user_id, data)
    settings = repository.settings.get_by_user_id(user_id)

    return make_response(
        True,
        "Settings updated successfully.",
        status_code=status.HTTP_200_OK,
        data=settings,
    )
