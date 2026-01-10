"""
Frontend serving routes.

This module provides routes to serve the React frontend application.
"""

from flask import Blueprint, render_template, send_from_directory
from pathlib import Path

frontend_bp = Blueprint("frontend", __name__)


@frontend_bp.route("/", defaults={"path": ""})
@frontend_bp.route("/<path:path>")
def serve_frontend(path: str):
    """
    Serve o frontend React para todas as rotas que não são da API.
    Isso permite que o React Router funcione corretamente.
    """
    # Se o caminho é um arquivo estático (assets), serve diretamente
    static_folder = Path("backend/static")
    if path and (static_folder / path).exists():
        return send_from_directory(str(static_folder), path)

    # Caso contrário, serve o index.html (SPA)
    return render_template("index.html")
