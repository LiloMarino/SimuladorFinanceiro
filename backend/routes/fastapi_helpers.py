"""
FastAPI-compatible response helpers to replace Flask's make_response.
"""

from typing import Any

from backend.types import JSONValue


def make_response_data(
    success: bool,
    message: str,
    data: JSONValue = None,
) -> dict[str, Any]:
    """
    Create standardized JSON response structure.
    Returns dict that FastAPI will automatically convert to JSONResponse.
    """
    return {
        "status": "success" if success else "error",
        "message": message,
        "data": data,
    }
