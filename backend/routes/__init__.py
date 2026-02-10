import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from backend.routes.auth import auth_router
from backend.routes.error import ERROR_500_RESPONSE, ErrorResponse
from backend.routes.frontend import register_frontend_routes
from backend.routes.importer import import_router
from backend.routes.operation import operation_router
from backend.routes.portfolio import portfolio_router
from backend.routes.realtime import realtime_router
from backend.routes.settings import settings_router
from backend.routes.simulation import simulation_router
from backend.routes.statistics import statistics_router
from backend.routes.timespeed import timespeed_router
from backend.routes.tunnel import tunnel_router

logger = logging.getLogger(__name__)


def register_routes(app: FastAPI):
    """Register all FastAPI routers and exception handlers."""
    app.include_router(operation_router, responses=ERROR_500_RESPONSE)
    app.include_router(portfolio_router, responses=ERROR_500_RESPONSE)
    app.include_router(settings_router, responses=ERROR_500_RESPONSE)
    app.include_router(import_router, responses=ERROR_500_RESPONSE)
    app.include_router(realtime_router, responses=ERROR_500_RESPONSE)
    app.include_router(timespeed_router, responses=ERROR_500_RESPONSE)
    app.include_router(auth_router, responses=ERROR_500_RESPONSE)
    app.include_router(statistics_router, responses=ERROR_500_RESPONSE)
    app.include_router(simulation_router, responses=ERROR_500_RESPONSE)
    app.include_router(tunnel_router, responses=ERROR_500_RESPONSE)

    # SPA FRONTEND (sempre por último para pegar todas as rotas não mapeadas)
    register_frontend_routes(app)

    @app.exception_handler(Exception)
    async def handle_error(request: Request, e: Exception):  # type: ignore
        """
        Exceções normais do python serão tratadas como Internal Server Error
        """
        logger.exception(f"{e.__class__.__name__}: {e}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message=str(e)).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, e: HTTPException):  # type: ignore
        """
        Exceções HTTP serão tratadas devidamente com seus respetivos status code
        """
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=e.detail).model_dump(),
        )
