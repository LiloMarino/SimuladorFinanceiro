from fastapi import Request

from backend.core.exceptions import SessionNotInitializedError


def get_client_id(request: Request) -> str:
    """
    Dependency que extrai o `client_id` do cookie.

    - Se não existir, lança SessionNotInitializedError
    """
    client_id = request.cookies.get("client_id")
    if not client_id:
        raise SessionNotInitializedError()
    return client_id
