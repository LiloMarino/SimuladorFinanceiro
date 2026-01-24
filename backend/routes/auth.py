import uuid

from fastapi import APIRouter, Request, Response, status
from pydantic import BaseModel

from backend.core import repository
from backend.core.dependencies import ClientID
from backend.core.dto.session import SessionDTO
from backend.core.dto.user import UserDTO
from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.http_exceptions import ConflictError, NotFoundError
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager

auth_router = APIRouter(prefix="/api", tags=["Authentication"])


class UserRegisterRequest(BaseModel):
    nickname: str


class UserClaimRequest(BaseModel):
    nickname: str


@auth_router.post(
    "/session/init",
    status_code=status.HTTP_204_NO_CONTENT,
)
def session_init(request: Request):
    """
    Garante que o cliente possua um client_id persistido no cookie.
    Se já existir → retorna o existente.
    Se não existir → cria um novo, salva no cookie e retorna.
    """
    client_id = request.cookies.get("client_id")

    if client_id:
        return

    response = Response(status_code=status.HTTP_204_NO_CONTENT)

    response.set_cookie(
        key="client_id",
        value=str(uuid.uuid4()),
        httponly=True,
        samesite="lax",
    )

    return response


@auth_router.get("/session/me", response_model=SessionDTO)
def session_me(client_id: ClientID):
    """
    Retorna os dados da sessão atual.
    """
    user_dto = UserManager.player_auth(client_id)

    session_dto = SessionDTO(
        authenticated=user_dto is not None,
        user=user_dto,
    )

    return session_dto


@auth_router.post("/session/logout", status_code=status.HTTP_204_NO_CONTENT)
def session_logout(client_id: ClientID):
    """
    Logout:
    - Remove presença
    - Invalida sessão no navegador
    """
    UserManager.player_logout(client_id)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        key="client_id",
        httponly=True,
        samesite="lax",
    )
    return response


@auth_router.post("/user/register", response_model=UserDTO)
def user_register(payload: UserRegisterRequest, client_id: ClientID):
    """
    Cria um usuário para o client_id atual.
    """
    nickname = payload.nickname

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
        starting = sim.settings.starting_cash
        sim._engine.add_cash(str(new_user.client_id), starting)

    return new_user


@auth_router.post("/user/claim", response_model=UserDTO)
def user_claim(payload: UserClaimRequest, client_id: ClientID):
    """
    Permite que o usuário recupere seu nickname após limpar navegador.
    """
    nickname = payload.nickname

    # Verificar se nickname existe
    existing_user = repository.user.get_by_nickname(nickname)
    if not existing_user:
        raise NotFoundError("Nickname does not exist.")

    # Verifica se usuário já está ativo em outro client
    active_players = UserManager.list_active_players()
    if any(u.id == existing_user.id for u in active_players):
        raise ConflictError("User is currently active and cannot be claimed.")

    # Atualizar client_id do usuário
    updated_user = repository.user.update_client_id(
        existing_user.id, uuid.UUID(client_id)
    )

    return updated_user


@auth_router.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
def user_delete(client_id: ClientID):
    """
    Remove o usuário atual permanentemente.
    Todos os dados relacionados serão deletados em cascade.
    """
    user = UserManager.get_user(client_id)
    if not user:
        raise NotFoundError("User not found.")
    UserManager.player_logout(client_id)

    # Deleta usuário do banco de dados
    repository.user.delete_user(user.id)

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        key="client_id",
        httponly=True,
        samesite="lax",
    )
    return response
