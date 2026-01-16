from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.core.logger import setup_logger
from backend.core.utils import resource_path

logger = setup_logger(__name__)

frontend_router = APIRouter()


def register_frontend_routes(app):
    """Registra rotas para servir o frontend SPA."""
    static_dir = resource_path("backend/static")

    if not static_dir.exists():
        logger.warning(f"Diretório de frontend não encontrado: {static_dir}")
        return

    logger.info(f"Servindo frontend estático de: {static_dir}")

    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/")
    async def serve_spa():
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return JSONResponse(
            status_code=404,
            content={
                "message": "Frontend não encontrado. Execute 'make build-frontend' primeiro.",
            },
        )

    @app.get("/{full_path:path}")
    async def serve_spa_routes(full_path: str):
        # Ignora rotas que começam com /api, /socket.io, /assets
        if full_path.startswith(("api/", "socket.io/", "assets/")):
            return JSONResponse(status_code=404, content={"message": "Not Found"})

        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return JSONResponse(
            status_code=404,
            content={
                "message": "Frontend não encontrado. Execute 'make build-frontend' primeiro.",
            },
        )
