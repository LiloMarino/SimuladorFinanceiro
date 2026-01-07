from werkzeug.exceptions import (
    BadRequest,
    Conflict,
    Forbidden,
    InternalServerError,
    NotFound,
    Unauthorized,
    UnprocessableEntity,
)

"""
Wrappers das exceções do werkzeug para auto-complete da IDE
"""


class BadRequestError(BadRequest):
    """400 Bad Request"""

    pass


class UnauthorizedError(Unauthorized):
    """401 Unauthorized"""

    pass


class ForbiddenError(Forbidden):
    """403 Forbidden"""

    pass


class NotFoundError(NotFound):
    """404 Not Found"""

    pass


class ConflictError(Conflict):
    """409 Conflict"""

    pass


class UnprocessableEntityError(UnprocessableEntity):
    """422 Unprocessable Entity"""

    pass


class InternalServerErrorError(InternalServerError):
    """500 Internal Server Error"""

    pass
