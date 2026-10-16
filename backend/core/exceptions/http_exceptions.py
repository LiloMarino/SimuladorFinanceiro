from fastapi import HTTPException


class BadRequestError(HTTPException):
    """400 Bad Request"""

    def __init__(
        self,
        detail: str = "O servidor não entendeu a requisição enviada.",
    ):
        super().__init__(status_code=400, detail=detail)


class UnauthorizedError(HTTPException):
    """401 Unauthorized"""

    def __init__(
        self,
        detail: str = "Não foi possível confirmar sua identidade. Entre novamente.",
    ):
        super().__init__(status_code=401, detail=detail)


class ForbiddenError(HTTPException):
    """403 Forbidden"""

    def __init__(
        self,
        detail: str = "Você não tem permissão para acessar este recurso.",
    ):
        super().__init__(status_code=403, detail=detail)


class NotFoundError(HTTPException):
    """404 Not Found"""

    def __init__(
        self,
        detail: str = "O recurso pedido não foi encontrado.",
    ):
        super().__init__(status_code=404, detail=detail)


class ConflictError(HTTPException):
    """409 Conflict"""

    def __init__(
        self,
        detail: str = (
            "O pedido conflita com o estado atual. O recurso pode ter sido"
            " alterado enquanto o pedido era processado."
        ),
    ):
        super().__init__(status_code=409, detail=detail)


class LockedError(HTTPException):
    """423 Locked"""

    def __init__(
        self,
        detail: str = "A sala está fechada para você agora.",
    ):
        super().__init__(status_code=423, detail=detail)


class UnprocessableEntityError(HTTPException):
    """422 Unprocessable Entity"""

    def __init__(
        self,
        detail: str = (
            "O pedido está bem formado, mas os dados enviados não podem ser"
            " processados."
        ),
    ):
        super().__init__(status_code=422, detail=detail)


class BadGatewayError(HTTPException):
    """502 Bad Gateway"""

    def __init__(
        self,
        detail: str = "Um serviço externo não respondeu ao pedido.",
    ):
        super().__init__(status_code=502, detail=detail)
