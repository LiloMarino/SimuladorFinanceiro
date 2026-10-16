from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str


class ValidationErrorItem(BaseModel):
    """Uma falha de validação, apontando o campo (`loc`) e a frase em português."""

    loc: list[str | int]
    msg: str
    type: str


class ValidationErrorResponse(ErrorResponse):
    """O erro padrão (`message`) mais a lista por campo, para marcar o formulário."""

    detail: list[ValidationErrorItem]


UNEXPECTED_ERROR_MESSAGE = "Ocorreu um erro inesperado no servidor."

# O Starlette levanta suas próprias HTTPException (rota inexistente, método errado)
# com o texto em inglês; aqui está o equivalente por status
STARLETTE_STATUS_MESSAGES = {
    404: "O endereço pedido não existe.",
    405: "Este endereço não aceita esse método.",
}
STARLETTE_FALLBACK_MESSAGE = "Não foi possível atender o pedido."

ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    422: {
        "model": ValidationErrorResponse,
    },
    500: {
        "model": ErrorResponse,
    },
}
