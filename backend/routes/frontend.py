"""
Frontend serving routes for FastAPI.

This module provides routes to serve the React frontend application.
"""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

frontend_router = APIRouter()

# Diretórios do backend (ajustados para PyInstaller)
import sys
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Rodando como executável PyInstaller
    base_path = Path(getattr(sys, "_MEIPASS"))
else:
    # Rodando como script Python normal
    base_path = Path(__file__).parent.parent.parent.resolve()

BACKEND_DIR = base_path / "backend"
STATIC_DIR = BACKEND_DIR / "static"
TEMPLATES_DIR = BACKEND_DIR / "templates"


@frontend_router.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """
    Serve o frontend React para todas as rotas que não são da API.
    
    FastAPI automaticamente serve arquivos estáticos montados via StaticFiles.
    Esta rota serve index.html para todas as outras rotas, permitindo que
    o React Router funcione corretamente (SPA).
    """
    # Serve index.html para permitir React Router
    index_path = TEMPLATES_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return FileResponse(STATIC_DIR / "index.html")
