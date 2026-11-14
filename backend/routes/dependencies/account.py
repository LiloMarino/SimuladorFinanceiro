from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header

from backend.features.simulation.simulation import Simulation
from backend.routes.dependencies.auth import get_client_id
from backend.routes.dependencies.simulation import get_active_simulation


def get_acting_client_id(
    client_id: Annotated[UUID, Depends(get_client_id)],
    simulation: Annotated[Simulation, Depends(get_active_simulation)],
    x_account: Annotated[
        int | None,
        Header(
            description="Id da gestora cuja conta opera o mercado; ausente, opera a conta do jogador."
        ),
    ] = None,
) -> UUID:
    """O client_id que opera: o do jogador, ou o da gestora que ele gere (header X-Account)."""
    return simulation.acting_client(client_id, x_account)
