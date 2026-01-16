from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from backend.core.logger import setup_logger
from backend.routes.auth import auth_router
from backend.routes.importer import import_router
from backend.routes.operation import operation_router
from backend.routes.portfolio import portfolio_router
from backend.routes.realtime import realtime_router
from backend.routes.settings import settings_router
from backend.routes.simulation import simulation_router
from backend.routes.statistics import statistics_router
from backend.routes.timespeed import timespeed_router

logger = setup_logger(__name__)


def register_routes(app: FastAPI):
    """Register all FastAPI routers and exception handlers."""
    app.include_router(operation_router)
    app.include_router(portfolio_router)
    app.include_router(settings_router)
    app.include_router(import_router)
    app.include_router(realtime_router)
    app.include_router(timespeed_router)
    app.include_router(auth_router)
    app.include_router(statistics_router)
    app.include_router(simulation_router)

    @app.exception_handler(Exception)
    async def handle_error(request: Request, e: Exception):  # type: ignore
        """
        Exceções normais do python serão tratadas como Internal Server Error
        """
        logger.exception(f"{e.__class__.__name__}: {e}")
        return JSONResponse(status_code=500, content={"message": str(e)})

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, e: HTTPException):  # type: ignore
        """
        Exceções HTTP serão tratadas devidamente com seus respetivos status code
        """
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
