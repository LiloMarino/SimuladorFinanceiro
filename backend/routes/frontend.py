"""
Frontend serving routes.

This module provides routes to serve the React frontend application.
"""

from flask import Blueprint, render_template

frontend_bp = Blueprint("frontend", __name__)


@frontend_bp.route("/", defaults={"path": ""})
@frontend_bp.route("/<path:path>")
def serve_frontend(path: str):
    """
    Serve o frontend React para todas as rotas que não são da API.
    
    Flask automaticamente serve arquivos estáticos (assets/, vite.svg) de
    static_folder devido à configuração static_url_path="" em main.py.
    
    Esta rota serve index.html para todas as outras rotas, permitindo que
    o React Router funcione corretamente (SPA).
    """
    return render_template("index.html")
