from fastapi.responses import JSONResponse

from backend.types import JSONValue


def make_response(
    success: bool,
    message: str,
    status_code: int = 200,
    data: JSONValue = None,
) -> JSONResponse:
    """Utility for standardized JSON API responses."""
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success" if success else "error",
            "message": message,
            "data": data,
        },
    )
