from flask import Blueprint, request

from backend.routes.helpers import make_response

auth_bp = Blueprint("auth", __name__)


# -------------------------------------------------------
# 1) SESSION INIT  (POST /api/session/init)
# -------------------------------------------------------
@auth_bp.route("/api/session/init", methods=["POST"])
def session_init():
    """
    Cria o client_id no cookie SE ele ainda não existe.
    Não retorna usuário, apenas (created: bool).
    """

    client_id = request.cookies.get("client_id")

    if client_id:
        # Cookie já existe → não cria novo
        return make_response(True, "Session already exists.", data={"created": False})

    # Criar nova sessão anônima
    new_client_id = create_anonymous_session()

    resp, status = make_response(True, "Session initialized.", data={"created": True})
    resp.set_cookie("client_id", new_client_id, httponly=True, samesite="Lax")

    return resp, status


# -------------------------------------------------------
# 2) SESSION ME  (GET /api/session/me)
# -------------------------------------------------------
@auth_bp.route("/api/session/me", methods=["GET"])
def session_me():
    """
    Retorna informações da sessão:
    - Se tem cookie
    - Se está associada a um usuário
    - Nickname caso exista
    """

    client_id = request.cookies.get("client_id")

    if not client_id:
        return make_response(False, "Session not initialized.", 401)

    user = find_user_by_client_id(client_id)

    return make_response(
        True,
        "Session data loaded.",
        data={
            "client_id": client_id,
            "authenticated": user is not None,
            "nickname": user.nickname if user else None,
        },
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
