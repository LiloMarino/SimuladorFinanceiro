from fastapi import HTTPException


class BadRequestError(HTTPException):
    """400 Bad Request"""

    def __init__(
        self,
        detail: str = (
            "The browser (or proxy) sent a request that this "
            "server could not understand."
        ),
    ):
        super().__init__(status_code=400, detail=detail)


class UnauthorizedError(HTTPException):
    """401 Unauthorized"""

    def __init__(
        self,
        detail: str = (
            "The server could not verify that you are authorized to access"
            " the URL requested. You either supplied the wrong credentials"
            " (e.g. a bad password), or your browser doesn't understand"
            " how to supply the credentials required."
        ),
    ):
        super().__init__(status_code=401, detail=detail)


class ForbiddenError(HTTPException):
    """403 Forbidden"""

    def __init__(
        self,
        detail: str = (
            "You don't have the permission to access the requested"
            " resource. It is either read-protected or not readable by the"
            " server."
        ),
    ):
        super().__init__(status_code=403, detail=detail)


class NotFoundError(HTTPException):
    """404 Not Found"""

    def __init__(
        self,
        detail: str = (
            "The requested URL was not found on the server. If you entered"
            " the URL manually please check your spelling and try again."
        ),
    ):
        super().__init__(status_code=404, detail=detail)


class ConflictError(HTTPException):
    """409 Conflict"""

    def __init__(
        self,
        detail: str = (
            "A conflict happened while processing the request. The resource "
            "might have been modified while the request was being processed."
        ),
    ):
        super().__init__(status_code=409, detail=detail)


class UnprocessableEntityError(HTTPException):
    """422 Unprocessable Entity"""

    def __init__(
        self,
        detail: str = (
            "The request was well-formed but was unable to be followed due"
            " to semantic errors."
        ),
    ):
        super().__init__(status_code=422, detail=detail)
