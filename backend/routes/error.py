from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str


ERROR_500_RESPONSE: dict[int | str, dict[str, Any]] = {
    500: {
        "model": ErrorResponse,
    }
}
