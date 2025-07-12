from flask import Blueprint, redirect, render_template, request

from backend.data_loader import importar_ativo

routes = Blueprint("routes", __name__)


@routes.route("/importar-ativo", methods=["POST"])
def importar_ativo_route():
    ticker = request.form.get("ticker")

    if ticker:
        sucesso, mensagem = importar_ativo(ticker)
        return render_template(
            "importar.html", status=mensagem
        )  # Mostra mensagem na tela
    return redirect("/")  # Ou volta para home
