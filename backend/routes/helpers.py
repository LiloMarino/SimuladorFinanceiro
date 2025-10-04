from flask import jsonify


def make_response(success: bool, message: str, data=None, status_code: int = 200):
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
