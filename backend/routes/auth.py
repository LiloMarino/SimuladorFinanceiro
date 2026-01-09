import uuid

from flask import Blueprint, request

from backend import config
from backend.core import repository
from backend.core.decorators.cookie import require_client_id
from backend.core.dto.session import SessionDTO
from backend.core.exceptions import NoActiveSimulationError
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.routes.helpers import make_response

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/session/init", methods=["POST"])
def session_init():
    """
    Garante que o cliente possua um client_id persistido no cookie.
    Se já existir → retorna o existente.
    Se não existir → cria um novo, salva no cookie e retorna.
    """

    client_id = request.cookies.get("client_id")

    if client_id:
        # Já possui sessão
        return make_response(
            True, "Session already exists.", data={"client_id": client_id}
        )

    # Criar nova sessão anônima
    new_client_id = str(uuid.uuid4())
    resp, status = make_response(
        True, "Session created.", data={"client_id": new_client_id}
    )

    # Seta cookie HttpOnly
    resp.set_cookie(
        "client_id",
        new_client_id,
        httponly=True,
        samesite="Lax",
    )

    return resp, status


@auth_bp.route("/api/session/me", methods=["GET"])
@require_client_id
def session_me(client_id: str):
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


@auth_bp.route("/api/session/logout", methods=["POST"])
def session_logout():
    """
    Remove o cookie de sessão atual.
    """
    resp, status = make_response(True, "Session logged out.")

    resp.set_cookie(
        "client_id",
        "",
        expires=0,
        httponly=True,
        samesite="Lax",
    )

    return resp, status


@auth_bp.route("/api/user/register", methods=["POST"])
@require_client_id
def user_register(client_id: str):
    """
    Cria um usuário para o client_id atual.
    """
    data = request.get_json()

    nickname = data.get("nickname")
    if not nickname:
        return make_response(False, "Nickname is required.", 422)

    # Verificar se já existe usuário com esse nickname
    existing_user = repository.user.get_by_nickname(nickname)
    if existing_user:
        return make_response(False, "User already registered for this client.", 409)

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

    return make_response(
        True,
        "User registered successfully.",
        data=new_user.to_json(),
    )


@auth_bp.route("/api/user/claim", methods=["POST"])
@require_client_id
def user_claim(client_id: str):
    """
    Permite que o usuário recupere seu nickname após limpar navegador.
    """
    data = request.get_json()

    nickname = data.get("nickname")
    if not nickname:
        return make_response(False, "Nickname is required.", 422)

    # Verificar se nickname existe
    existing_user = repository.user.get_by_nickname(nickname)
    if not existing_user:
        return make_response(False, "Nickname does not exist.", 404)

    # Verifica se usuário já está ativo em outro client
    active_players = UserManager.list_active_players()
    if any(u.id == existing_user.id for u in active_players):
        return make_response(
            False,
            "User is currently active and cannot be claimed.",
            409,
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
