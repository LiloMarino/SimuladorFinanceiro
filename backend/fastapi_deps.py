"""
FastAPI dependencies to replace Flask decorators.
"""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status

from backend.config.toml_settings import load_toml_settings
from backend.core.exceptions import NoActiveSimulationError
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.simulation.simulation import Simulation


def get_client_id_from_cookie(client_id: Annotated[str | None, Cookie()] = None) -> str:
    """
    FastAPI dependency that extracts client_id from cookie.
    Replaces @require_client_id decorator.
    """
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not initialized. client_id cookie missing.",
        )
    return client_id


def get_active_simulation() -> Simulation:
    """
    FastAPI dependency that gets the active simulation.
    Replaces @require_simulation decorator.
    """
    try:
        return SimulationManager.get_active_simulation()
    except NoActiveSimulationError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active simulation found.",
        ) from e


def require_host(client_id: Annotated[str | None, Cookie()] = None) -> None:
    """
    FastAPI dependency that checks if user is the host.
    Replaces @require_host decorator.
    """
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not initialized.",
        )

    user = UserManager.get_user(client_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    settings = load_toml_settings()
    host_nickname = settings.host.nickname

    if user.nickname != host_nickname:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o host pode executar essa ação.",
        )


# Type aliases for convenience
ClientID = Annotated[str, Depends(get_client_id_from_cookie)]
ActiveSimulation = Annotated[Simulation, Depends(get_active_simulation)]
HostOnly = Annotated[None, Depends(require_host)]
