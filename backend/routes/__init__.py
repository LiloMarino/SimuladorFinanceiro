from flask import Flask
from werkzeug.exceptions import HTTPException

from backend.core.logger import setup_logger
from backend.routes.auth import auth_bp
from backend.routes.helpers import make_response
from backend.routes.importer import import_bp
from backend.routes.operation import operation_bp
from backend.routes.portfolio import portfolio_bp
from backend.routes.realtime import realtime_bp
from backend.routes.settings import settings_bp
from backend.routes.simulation import simulation_bp
from backend.routes.statistics import statistics_bp
from backend.routes.timespeed import timespeed_bp

logger = setup_logger(__name__)


def register_routes(app: Flask):
    """Register all route blueprints."""
    app.register_blueprint(operation_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(import_bp)
    app.register_blueprint(realtime_bp)
    app.register_blueprint(timespeed_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(simulation_bp)

    @app.errorhandler(Exception)
    def handle_error(e):  # type: ignore
        logger.exception(f"{e.__class__.__name__}: {e}")
        return make_response(False, str(e), 500)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        return make_response(
            False,
            e.description or e.name,
            status_code=e.code or 500,
        )
