from functools import wraps

from flask import request

from backend.core.exceptions import SessionNotInitializedError


def require_client_id(func):
    """
    Decorator que injeta o `client_id` do cookie como keyword argument `client_id`.

    - Se o cookie 'client_id' não existir, lança `SessionNotInitializedError`.
    - Pode ser usado em qualquer posição na assinatura da função.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        client_id = request.cookies.get("client_id")
        if not client_id:
            raise SessionNotInitializedError()
        kwargs["client_id"] = client_id
        return func(*args, **kwargs)

    return wrapper
