import uuid

from flask import Blueprint, request

from backend.core import repository
from backend.core.dto.session import SessionDTO
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
def session_me():
    """
    Retorna informações da sessão atual.
    """

    client_id = request.cookies.get("client_id")

    if not client_id:
        return make_response(
            False,
            "Session not initialized.",
            status_code=401,
        )

    # Busca informações do usuário
    user_dto = repository.user.get_by_client_id(client_id)
    session_dto = SessionDTO(
        authenticated=user_dto is not None,
        user=user_dto,
    )

    return make_response(
        True,
        "Session data loaded.",
        data=session_dto.to_json(),
    )


@auth_bp.route("/api/user/register", methods=["POST"])
def user_register():
    """
    Cria um usuário para o client_id atual.
    """
    data = request.get_json()

    nickname = data.get("nickname")
    if not nickname:
        return make_response(False, "Nickname is required.", 422)

    client_id = request.cookies.get("client_id")
    if not client_id:
        return make_response(False, "Session not initialized.", 401)

    # Verificar se já existe usuário com esse nickname
    existing_user = repository.user.get_by_nickname(nickname)
    if existing_user:
        return make_response(False, "User already registered for this client.", 409)

    # Cria novo usuário
    new_user = repository.user.create_user(client_id, nickname)

    return make_response(
        True,
        "User registered successfully.",
        data=new_user.to_json(),
    )


@auth_bp.route("/api/user/claim", methods=["POST"])
def user_claim():
    """
    Permite que o usuário recupere seu nickname após limpar navegador.
    """
    data = request.get_json()

    nickname = data.get("nickname")
    if not nickname:
        return make_response(False, "Nickname is required.", 422)

    client_id = request.cookies.get("client_id")
    if not client_id:
        return make_response(False, "Session not initialized.", 401)

    # Verificar se nickname existe
    existing_user = repository.user.get_by_nickname(nickname)
    if not existing_user:
        return make_response(False, "Nickname does not exist.", 404)

    # Atualizar client_id do usuário para o novo navegador
    updated_user = repository.user.update_client_id(
        existing_user.id, uuid.UUID(client_id)
    )

    return make_response(
        True,
        "Nickname claimed successfully.",
        data=updated_user.to_json(),
    )
