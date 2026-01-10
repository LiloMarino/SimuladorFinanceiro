from typing import Annotated

from fastapi import Depends

from backend.core.dependencies.auth import get_client_id, get_current_user, verify_host
from backend.core.dependencies.simulation import get_active_simulation
from backend.core.dto.user import UserDTO
from backend.features.simulation.simulation import Simulation

ClientID = Annotated[str, Depends(get_client_id)]
CurrentUser = Annotated[UserDTO, Depends(get_current_user)]
HostVerified = Annotated[None, Depends(verify_host)]
ActiveSimulation = Annotated[Simulation, Depends(get_active_simulation)]
