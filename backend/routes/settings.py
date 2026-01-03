from flask import Blueprint, request

from backend.core import repository
from backend.core.decorators.cookie import require_client_id
from backend.core.runtime.user_manager import UserManager
from backend.routes.helpers import make_response

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/api/settings", methods=["GET"])
@require_client_id
def get_settings(client_id):
    settings = repository.settings.get_by_user_id(UserManager.get_user_id(client_id))
    return make_response(
        True,
        "Settings loaded successfully.",
        200,
        settings,
    )


@settings_bp.route("/api/settings", methods=["PUT"])
@require_client_id
def update_settings(client_id):
    data = request.get_json()

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
