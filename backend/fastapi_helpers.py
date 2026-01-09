"""
FastAPI response helpers.
"""


from fastapi import status
from fastapi.responses import JSONResponse

from backend.types import JSONValue


def make_response(
    success: bool,
    message: str,
    status_code: int = status.HTTP_200_OK,
    data: JSONValue = None,
) -> JSONResponse:
    """
    Utility for standardized JSON API responses in FastAPI.
    Maintains compatibility with the original Flask response format.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success" if success else "error",
            "message": message,
            "data": data,
        },
    )
