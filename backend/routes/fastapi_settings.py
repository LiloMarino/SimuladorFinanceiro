"""
User settings routes for FastAPI.
Migrated from Flask Blueprint to FastAPI APIRouter.
"""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from backend.core import repository
from backend.core.dependencies import ClientID
from backend.core.exceptions.fastapi_exceptions import BadRequestError
from backend.core.runtime.user_manager import UserManager
from backend.routes.fastapi_helpers import make_response_data

router = APIRouter(prefix="/api", tags=["settings"])


class UpdateSettingsRequest(BaseModel):
    settings: dict[str, Any]


@router.get("/settings")
async def get_settings(client_id: ClientID):
    """Get user settings."""
    settings = repository.settings.get_by_user_id(UserManager.get_user_id(client_id))
    return make_response_data(
        True,
        "Settings loaded successfully.",
        data=settings,
    )


@router.put("/settings")
async def update_settings(request: UpdateSettingsRequest, client_id: ClientID):
    """Update user settings."""
    data = request.settings

    if not isinstance(data, dict):
        raise BadRequestError("Invalid settings payload.")

    user_id = UserManager.get_user_id(client_id)

    repository.settings.update_by_user_id(user_id, data)
    settings = repository.settings.get_by_user_id(user_id)

    return make_response_data(
        True,
        "Settings updated successfully.",
        data=settings,
    )
