from flask import Flask

from backend.core.logger import setup_logger
from backend.routes.auth import auth_bp
from backend.routes.helpers import make_response
from backend.routes.import_routes import import_bp
from backend.routes.operation_routes import operation_bp
from backend.routes.portfolio_routes import portfolio_bp
from backend.routes.realtime_routes import realtime_bp
from backend.routes.settings_routes import settings_bp
from backend.routes.timespeed_routes import timespeed_bp

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

    @app.errorhandler(Exception)
    def handle_error(e):  # type: ignore
        logger.exception(f"{e.__class__.__name__}: {e}")
        return make_response(False, str(e), 500)
