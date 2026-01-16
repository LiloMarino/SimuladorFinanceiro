import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

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

    # ------------------------------------------------------------
    # Servir frontend estático (para o executável)
    # ------------------------------------------------------------
    # Detecta se está rodando em um executável PyInstaller
    if getattr(sys, "frozen", False):
        # Rodando no executável
        base_path = Path(sys._MEIPASS)  # type: ignore
    else:
        # Rodando em desenvolvimento
        base_path = Path(__file__).parent.parent.parent

    static_dir = base_path / "backend" / "static"
    templates_dir = base_path / "backend" / "templates"

    if static_dir.exists() and templates_dir.exists():
        logger.info(f"Servindo frontend estático de: {static_dir}")

        # Serve os arquivos estáticos (CSS, JS, imagens, etc.)
        app.mount(
            "/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets"
        )

        # Serve o index.html na raiz
        @app.get("/")
        async def serve_spa():
            index_path = templates_dir / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            return JSONResponse(
                status_code=404,
                content={
                    "message": "Frontend não encontrado. Execute 'make build-frontend' primeiro."
                },
            )

        # Captura todas as outras rotas não-API e serve o index.html (para SPA routing)
        @app.get("/{full_path:path}")
        async def serve_spa_routes(full_path: str):
            # Ignora rotas que começam com /api, /socket.io, /assets
            if full_path.startswith(("api/", "socket.io/", "assets/")):
                return JSONResponse(status_code=404, content={"message": "Not Found"})

            index_path = templates_dir / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            return JSONResponse(
                status_code=404,
                content={
                    "message": "Frontend não encontrado. Execute 'make build-frontend' primeiro."
                },
            )
    else:
        logger.warning(
            f"Diretórios de frontend não encontrados. "
            f"Static: {static_dir.exists()}, Templates: {templates_dir.exists()}"
        )
