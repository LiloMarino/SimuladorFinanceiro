import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.routes.achievements import achievements_router
from backend.routes.auth import auth_router
from backend.routes.backtest import backtest_router
from backend.routes.candle_challenge import candle_challenge_router
from backend.routes.correlation import correlation_router
from backend.routes.credit import credit_router
from backend.routes.debug import debug_router
from backend.routes.error import (
    ERROR_RESPONSES,
    STARLETTE_FALLBACK_MESSAGE,
    STARLETTE_STATUS_MESSAGES,
    UNEXPECTED_ERROR_MESSAGE,
    ErrorResponse,
    ValidationErrorResponse,
)
from backend.routes.frontend import register_frontend_routes
from backend.routes.government import government_router
from backend.routes.importer import import_router
from backend.routes.news import news_router
from backend.routes.operation import operation_router
from backend.routes.pending import pending_router
from backend.routes.portfolio import portfolio_router
from backend.routes.presets import presets_router
from backend.routes.realtime import realtime_router
from backend.routes.settings import settings_router
from backend.routes.simulation import simulation_router
from backend.routes.statistics import statistics_router
from backend.routes.strategy import strategy_router
from backend.routes.summaries import summaries_router
from backend.routes.timespeed import timespeed_router
from backend.routes.tunnel import tunnel_router
from backend.routes.validation_messages import format_validation_errors, to_items
from backend.routes.version import version_router

logger = logging.getLogger(__name__)


def register_routes(app: FastAPI):
    """Register all FastAPI routers and exception handlers."""
    app.include_router(operation_router, responses=ERROR_RESPONSES)
    app.include_router(portfolio_router, responses=ERROR_RESPONSES)
    app.include_router(settings_router, responses=ERROR_RESPONSES)
    app.include_router(import_router, responses=ERROR_RESPONSES)
    app.include_router(realtime_router, responses=ERROR_RESPONSES)
    app.include_router(timespeed_router, responses=ERROR_RESPONSES)
    app.include_router(auth_router, responses=ERROR_RESPONSES)
    app.include_router(statistics_router, responses=ERROR_RESPONSES)
    app.include_router(achievements_router, responses=ERROR_RESPONSES)
    app.include_router(summaries_router, responses=ERROR_RESPONSES)
    app.include_router(news_router, responses=ERROR_RESPONSES)
    app.include_router(pending_router, responses=ERROR_RESPONSES)
    app.include_router(correlation_router, responses=ERROR_RESPONSES)
    app.include_router(credit_router, responses=ERROR_RESPONSES)
    app.include_router(government_router, responses=ERROR_RESPONSES)
    app.include_router(strategy_router, responses=ERROR_RESPONSES)
    app.include_router(simulation_router, responses=ERROR_RESPONSES)
    app.include_router(candle_challenge_router, responses=ERROR_RESPONSES)
    app.include_router(backtest_router, responses=ERROR_RESPONSES)
    app.include_router(presets_router, responses=ERROR_RESPONSES)
    app.include_router(tunnel_router, responses=ERROR_RESPONSES)
    app.include_router(version_router, responses=ERROR_RESPONSES)
    app.include_router(debug_router, responses=ERROR_RESPONSES)

    # SPA FRONTEND (sempre por último para pegar todas as rotas não mapeadas)
    register_frontend_routes(app)

    @app.exception_handler(Exception)
    async def handle_error(request: Request, e: Exception):
        """
        Exceções normais do python serão tratadas como Internal Server Error
        """
        logger.error("%s: %s", e.__class__.__name__, e, exc_info=e)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message=UNEXPECTED_ERROR_MESSAGE).model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, e: StarletteHTTPException):
        """
        Exceções HTTP serão tratadas devidamente com seus respetivos status code
        """
        # O `detail` das exceções do projeto já é em português; o das do Starlette não
        if isinstance(e, HTTPException):
            message = str(e.detail)
        else:
            message = STARLETTE_STATUS_MESSAGES.get(
                e.status_code, STARLETTE_FALLBACK_MESSAGE
            )
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=message).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, e: RequestValidationError):
        """
        Falhas de validação viram uma frase em português (`message`, o que o
        frontend mostra) mais a lista por campo (`detail`)
        """
        errors = e.errors()
        return JSONResponse(
            status_code=422,
            content=ValidationErrorResponse(
                message=format_validation_errors(errors),
                detail=to_items(errors),
            ).model_dump(),
        )
