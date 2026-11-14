from typing import Annotated
from uuid import UUID

from fastapi import Depends

from backend.core.dto.user import UserDTO
from backend.features.simulation.simulation import Simulation
from backend.routes.dependencies.account import get_acting_client_id
from backend.routes.dependencies.auth import (
    get_client_id,
    get_current_user,
    verify_host,
)
from backend.routes.dependencies.simulation import get_active_simulation

ClientID = Annotated[UUID, Depends(get_client_id)]
# Conta que opera o mercado: a do jogador, ou a da gestora do header X-Account
ActingClient = Annotated[UUID, Depends(get_acting_client_id)]
CurrentUser = Annotated[UserDTO, Depends(get_current_user)]
HostVerified = Annotated[None, Depends(verify_host)]
ActiveSimulation = Annotated[Simulation, Depends(get_active_simulation)]
