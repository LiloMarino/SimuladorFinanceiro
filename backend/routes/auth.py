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


# -------------------------------------------------------
# 3) REGISTER (POST /api/user/register)
# -------------------------------------------------------
@auth_bp.route("/api/user/register", methods=["POST"])
def user_register():
    """
    Cria um usuário anônimo NO BD associado ao client_id já existente.
    """

    client_id = request.cookies.get("client_id")

    if not client_id:
        return make_response(False, "Session not initialized.", 401)

    user = register_user(client_id)

    return make_response(
        True,
        "User registered successfully.",
        data={"client_id": client_id, "user_id": user.id},
    )


# -------------------------------------------------------
# 4) CLAIM NICKNAME  (POST /api/user/claim)
# -------------------------------------------------------
@auth_bp.route("/api/user/claim", methods=["POST"])
def user_claim():
    """
    O usuário escolhe um nickname.
    Valida se está livre, associa ao user.
    """

    data = request.get_json(force=True)
    nickname = data.get("nickname")

    if not nickname:
        return make_response(False, "Nickname is required.", 422)

    client_id = request.cookies.get("client_id")

    if not client_id:
        return make_response(False, "Session not initialized.", 401)

    success, message = claim_nickname(client_id, nickname)

    if not success:
        return make_response(False, message, 409)

    return make_response(
        True, "Nickname claimed successfully.", data={"nickname": nickname}
    )
