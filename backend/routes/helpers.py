from flask import jsonify

from backend.types import JSONValue


def make_response(
    success: bool,
    message: str,
    status_code: int = 200,
    data: JSONValue = None,
):
    """Utility for standardized JSON API responses."""
    return (
        jsonify(
            {
                "status": "success" if success else "error",
                "message": message,
                "data": data,
            }
        ),
        status_code,
    )
