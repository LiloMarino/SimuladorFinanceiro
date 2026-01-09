"""
Authentication and session management routes for FastAPI.
Migrated from Flask Blueprint to FastAPI APIRouter.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Cookie, Response
from pydantic import BaseModel

from backend import config
from backend.core import repository
from backend.core.dependencies import ClientID
from backend.core.dto.session import SessionDTO
from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.fastapi_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.routes.fastapi_helpers import make_response_data

router = APIRouter(prefix="/api", tags=["auth"])


# Request/Response models
class RegisterRequest(BaseModel):
    nickname: str


class ClaimRequest(BaseModel):
    nickname: str


@router.post("/session/init")
async def session_init(
    response: Response,
    client_id: Annotated[str | None, Cookie()] = None
):
    """
    Garante que o cliente possua um client_id persistido no cookie.
    Se já existir → retorna o existente.
    Se não existir → cria um novo, salva no cookie e retorna.

    Note: client_id comes from Cookie but is optional for this endpoint.
    """
    # If already has session
    if client_id:
        return make_response_data(
            True, "Session already exists.", data={"client_id": client_id}
        )

    # Create new anonymous session
    new_client_id = str(uuid.uuid4())

    # Set HttpOnly cookie
    response.set_cookie(
        key="client_id",
        value=new_client_id,
        httponly=True,
        samesite="lax",
    )

    return make_response_data(
        True, "Session created.", data={"client_id": new_client_id}
    )


@router.get("/session/me")
async def session_me(client_id: ClientID):
    """
    Retorna os dados da sessão atual.
    """
    user_dto = UserManager.player_auth(client_id)

    session_dto = SessionDTO(
        authenticated=user_dto is not None,
        user=user_dto,
    )

    return make_response_data(
        True,
        "Session data loaded.",
        data=session_dto.to_json(),
    )


@router.post("/session/logout")
async def session_logout(response: Response):
    """
    Remove o cookie de sessão atual.
    """
    response.set_cookie(
        key="client_id",
        value="",
        expires=0,
        httponly=True,
        samesite="lax",
    )

    return make_response_data(True, "Session logged out.")


@router.post("/user/register")
async def user_register(request: RegisterRequest, client_id: ClientID):
    """
    Cria um usuário para o client_id atual.
    """
    nickname = request.nickname
    if not nickname:
        raise UnprocessableEntityError("Nickname is required.")

    # Verificar se já existe usuário com esse nickname
    existing_user = repository.user.get_by_nickname(nickname)
    if existing_user:
        raise ConflictError("User already registered for this client.")

    # Cria novo usuário
    new_user = repository.user.create_user(client_id, nickname)

    # Se houver uma simulação ativa, concede o depósito inicial usando o SimulationEngine
    try:
        sim = SimulationManager.get_active_simulation()
    except NoActiveSimulationError:
        sim = None

    if sim:
        starting = float(config.toml.simulation.starting_cash)
        sim._engine.add_cash(str(new_user.client_id), starting)

    return make_response_data(
        True,
        "User registered successfully.",
        data=new_user.to_json(),
    )


@router.post("/user/claim")
async def user_claim(request: ClaimRequest, client_id: ClientID):
    """
    Permite que o usuário recupere seu nickname após limpar navegador.
    """
    nickname = request.nickname
    if not nickname:
        raise UnprocessableEntityError("Nickname is required.")

    # Verificar se nickname existe
    existing_user = repository.user.get_by_nickname(nickname)
    if not existing_user:
        raise NotFoundError("Nickname does not exist.")

    # Verifica se usuário já está ativo em outro client
    active_players = UserManager.list_active_players()
    if any(u.id == existing_user.id for u in active_players):
        raise ConflictError(
            "User is currently active and cannot be claimed.",
        )

    # Atualizar client_id do usuário
    updated_user = repository.user.update_client_id(
        existing_user.id, uuid.UUID(client_id)
    )

    return make_response_data(
        True,
        "Nickname claimed successfully.",
        data=updated_user.to_json(),
    )
