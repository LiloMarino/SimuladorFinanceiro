"""
FastAPI dependencies that replace Flask decorators.
These inject parameters into route handlers via Depends().
"""

from typing import Annotated

from fastapi import Cookie, Depends

from backend.config.toml_settings import load_toml_settings
from backend.core.exceptions import SessionNotInitializedError
from backend.core.exceptions.fastapi_exceptions import ForbiddenError, NotFoundError
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.simulation.simulation import Simulation


def get_client_id(client_id: Annotated[str | None, Cookie()] = None) -> str:
    """
    Dependency that extracts and validates client_id from cookie.
    Replaces @require_client_id decorator.
    """
    if not client_id:
        raise SessionNotInitializedError()
    return client_id


def get_simulation() -> Simulation:
    """
    Dependency that gets the active simulation.
    Replaces @require_simulation decorator.
    """
    return SimulationManager.get_active_simulation()


def verify_host(client_id: Annotated[str, Depends(get_client_id)]) -> None:
    """
    Dependency that verifies user is the host.
    Replaces @require_host decorator.
    """
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")

    settings = load_toml_settings()
    host_nickname = settings.host.nickname

    if user.nickname != host_nickname:
        raise ForbiddenError("Apenas o host pode executar essa ação.")


# Type aliases for common dependencies
ClientID = Annotated[str, Depends(get_client_id)]
ActiveSimulation = Annotated[Simulation, Depends(get_simulation)]
HostVerified = Annotated[None, Depends(verify_host)]
