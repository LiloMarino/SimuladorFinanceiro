from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.core.logger import setup_logger
from backend.core.utils import resource_path

logger = setup_logger(__name__)


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
    @app.get("/{full_path:path}")
    async def spa_fallback(request: Request, full_path: str):  # type: ignore
        """
        Qualquer rota não capturada acima devolve o index.html
        """
        index_file = static_dir / "index.html"
        return FileResponse(index_file)
