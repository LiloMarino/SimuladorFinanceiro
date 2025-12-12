from collections.abc import Callable
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar

from flask import request


class SessionNotInitializedError(Exception):
    """Raised when client_id cookie is missing."""

    pass


P = ParamSpec("P")
R = TypeVar("R")


def require_client_id(
    func: Callable[Concatenate[str, P], R],
) -> Callable[P, R]:
    """
    Decorator que injeta o client_id como primeiro argumento da função.
    Exige que o cookie 'client_id' exista, caso contrário retorna HTTP 401.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        client_id = request.cookies.get("client_id")

        if not client_id:
            raise SessionNotInitializedError()

        return func(client_id, *args, **kwargs)

    return wrapper
