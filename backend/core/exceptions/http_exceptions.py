from fastapi import HTTPException, status

"""
FastAPI-compatible HTTP exceptions.
These replace the Werkzeug exceptions used in Flask.
"""


class HTTPError(HTTPException):
    """Base class for all HTTP errors - used for exception handler"""

    pass


class BadRequestError(HTTPError):
    """400 Bad Request"""

    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedError(HTTPError):
    """401 Unauthorized"""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenError(HTTPError):
    """403 Forbidden"""

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundError(HTTPError):
    """404 Not Found"""

    def __init__(self, detail: str = "Not Found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictError(HTTPError):
    """409 Conflict"""

    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UnprocessableEntityError(HTTPError):
    """422 Unprocessable Entity"""

    def __init__(self, detail: str = "Unprocessable Entity"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )
