import uuid

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel

from backend import config
from backend.core import repository
from backend.core.dto.session import SessionDTO
from backend.core.exceptions import NoActiveSimulationError
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.fastapi_deps import ClientID, get_client_id_from_cookie
from backend.fastapi_helpers import make_response

auth_router = APIRouter(prefix="/api", tags=["auth"])


# Request models
class RegisterUserRequest(BaseModel):
    nickname: str


class ClaimUserRequest(BaseModel):
    nickname: str


@auth_router.post("/session/init")
def session_init(response: Response, client_id: str | None = None):
    """
    Garante que o cliente possua um client_id persistido no cookie.
    Se já existir → retorna o existente.
    Se não existir → cria um novo, salva no cookie e retorna.
    """
    # Try to get client_id from cookie
    if client_id:
        try:
            client_id = get_client_id_from_cookie(client_id)
            # Já possui sessão
            return make_response(
                True, "Session already exists.", data={"client_id": client_id}
            )
        except HTTPException:
            pass  # Cookie não válido, criar nova sessão

    # Criar nova sessão anônima
    new_client_id = str(uuid.uuid4())

    # Seta cookie HttpOnly
    response.set_cookie(
        key="client_id",
        value=new_client_id,
        httponly=True,
        samesite="lax",
    )

    return make_response(
        True, "Session created.", data={"client_id": new_client_id}
    )


@auth_router.get("/session/me")
def session_me(client_id: ClientID):
    """
    Retorna os dados da sessão atual.
    """
    user_dto = UserManager.player_auth(client_id)

    session_dto = SessionDTO(
        authenticated=user_dto is not None,
        user=user_dto,
    )

    return make_response(
        True,
        "Session data loaded.",
        data=session_dto.to_json(),
    )


@auth_router.post("/session/logout")
def session_logout(response: Response):
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

    return make_response(True, "Session logged out.")


@auth_router.post("/user/register")
def user_register(client_id: ClientID, payload: RegisterUserRequest):
    """
    Cria um usuário para o client_id atual.
    """
    if not payload.nickname:
        return make_response(
            False,
            "Nickname is required.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # Verificar se já existe usuário com esse nickname
    existing_user = repository.user.get_by_nickname(payload.nickname)
    if existing_user:
        return make_response(
            False,
            "User already registered for this client.",
            status_code=status.HTTP_409_CONFLICT,
        )

    # Cria novo usuário
    new_user = repository.user.create_user(client_id, payload.nickname)

    # Se houver uma simulação ativa, concede o depósito inicial usando o SimulationEngine
    try:
        sim = SimulationManager.get_active_simulation()
    except NoActiveSimulationError:
        sim = None

    if sim:
        starting = float(config.toml.simulation.starting_cash)
        sim._engine.add_cash(str(new_user.client_id), starting)

    return make_response(
        True,
        "User registered successfully.",
        data=new_user.to_json(),
    )


@auth_router.post("/user/claim")
def user_claim(client_id: ClientID, payload: ClaimUserRequest):
    """
    Permite que o usuário recupere seu nickname após limpar navegador.
    """
    if not payload.nickname:
        return make_response(
            False,
            "Nickname is required.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # Verificar se nickname existe
    existing_user = repository.user.get_by_nickname(payload.nickname)
    if not existing_user:
        return make_response(
            False, "Nickname does not exist.", status_code=status.HTTP_404_NOT_FOUND
        )

    # Verifica se usuário já está ativo em outro client
    active_players = UserManager.list_active_players()
    if any(u.id == existing_user.id for u in active_players):
        return make_response(
            False,
            "User is currently active and cannot be claimed.",
            status_code=status.HTTP_409_CONFLICT,
        )

    # Atualizar client_id do usuário
    updated_user = repository.user.update_client_id(
        existing_user.id, uuid.UUID(client_id)
    )

    return make_response(
        True,
        "Nickname claimed successfully.",
        data=updated_user.to_json(),
    )
