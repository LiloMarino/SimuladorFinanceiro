import logging

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.core.utils import resource_path

logger = logging.getLogger(__name__)


def register_frontend_routes(app: FastAPI):
    """Registra rotas para servir o frontend SPA."""
    static_dir = resource_path("backend/static")

    if not static_dir.exists():
        logger.warning(f"Frontend não encontrado em {static_dir}")
        return

    logger.info(f"Servindo frontend SPA de {static_dir}")
    app.mount(
        "/static",
        StaticFiles(directory=static_dir, html=True),
        name="frontend",
    )

    # SPA fallback (React Router)
    @app.get(
        "/{full_path:path}",
        summary="SPA fallback",
        description="Rota de fallback para o Single Page Application (SPA) - devolve index.html para rotas não capturadas.",
        include_in_schema=False,
    )
    async def spa_fallback(request: Request, full_path: str):  # type: ignore
        """
        Fallback para rotas não capturadas do SPA.
        """
        index_file = static_dir / "index.html"
        return FileResponse(index_file)
