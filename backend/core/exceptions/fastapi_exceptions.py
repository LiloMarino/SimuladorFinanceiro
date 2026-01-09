"""
FastAPI-compatible HTTP exceptions to replace Werkzeug exceptions.
These maintain the same status codes and descriptions as the original Werkzeug exceptions.
"""

from fastapi import HTTPException


class BadRequestError(HTTPException):
    """400 Bad Request"""

    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=400, detail=detail)


class UnauthorizedError(HTTPException):
    """401 Unauthorized"""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenError(HTTPException):
    """403 Forbidden"""

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail=detail)


class NotFoundError(HTTPException):
    """404 Not Found"""

    def __init__(self, detail: str = "Not Found"):
        super().__init__(status_code=404, detail=detail)


class ConflictError(HTTPException):
    """409 Conflict"""

    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=409, detail=detail)


class UnprocessableEntityError(HTTPException):
    """422 Unprocessable Entity"""

    def __init__(self, detail: str = "Unprocessable Entity"):
        super().__init__(status_code=422, detail=detail)
