from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from backend.data_loader import update_from_csv, update_from_yfinance
from backend.simulation import get_simulation

routes = Blueprint("routes", __name__)

# ----------
# Páginas
# ----------


@routes.route("/", methods=["GET"])
def index():
    return redirect(url_for("routes.portfolio"))


@routes.route("/renda-variavel", methods=["GET"])
def variable_income():
    simulation = get_simulation()
    return render_template(
        "renda_variavel.html",
        stocks=simulation.get_stocks(),
        active_page=variable_income.__name__,
    )


@routes.route("/renda-fixa", methods=["GET"])
def fixed_income():
    return render_template("renda_fixa.html", active_page=fixed_income.__name__)


@routes.route("/carteira", methods=["GET"])
def portfolio():
    return render_template("carteira.html", active_page=portfolio.__name__)


@routes.route("/importar-ativos", methods=["GET", "POST"])
def import_assets():
    if request.method == "POST":
        action = request.form.get("action")
        overwrite = request.form.get("overwrite") == "on"

        try:
            if action == "yfinance":
                ticker = request.form.get("ticker")
                if not ticker:
                    flash("Você precisa fornecer o código do ativo!", "warning")
                else:
                    update_from_yfinance(ticker, overwrite=overwrite)
                    flash(
                        f"Ativo '{ticker}' importado com sucesso!"
                        + (" (sobrescrito)" if overwrite else ""),
                        "success",
                    )

            elif action == "csv":
                ticker = request.form.get("ticker")
                file = request.files.get("csv_file")

                if not ticker:
                    flash("Você precisa fornecer o nome do ativo!", "warning")
                elif not file:
                    flash("Você precisa selecionar um arquivo CSV!", "warning")
                else:
                    update_from_csv(file, ticker, overwrite=overwrite)
                    flash(
                        f"Arquivo CSV do ativo '{ticker}' importado com sucesso!"
                        + (" (sobrescrito)" if overwrite else ""),
                        "success",
                    )

            else:
                flash("Ação inválida.", "danger")

        except Exception as e:
            flash(f"Erro ao importar: {str(e)}", "danger")

        return redirect(url_for("routes.import_assets"))

    return render_template("importar_ativos.html", active_page=import_assets.__name__)


@routes.route("/renda-variavel/<string:ativo>", methods=["GET"])
def variable_income_details(ativo):
    simulation = get_simulation()
    stock = simulation.get_stock_details(ativo)
    if not stock:
        return "Ativo não encontrado", 404

    return render_template(
        "detalhe_renda_variavel.html",
        stock=stock,
        active_page=variable_income.__name__,
    )


@routes.route("/renda-fixa/<string:ativo>", methods=["GET"])
def fixed_income_details(ativo):
    return render_template(
        "detalhe_renda_fixa.html", ativo=ativo, active_page=fixed_income.__name__
    )


@routes.route("/estrategia", methods=["GET"])
def strategies():
    return render_template("estrategias.html", active_page=strategies.__name__)


@routes.route("/estatisticas", methods=["GET"])
def statistics():
    return render_template("estatisticas.html", active_page=statistics.__name__)


@routes.route("/lobby", methods=["GET"])
def lobby():
    return render_template("lobby.html", active_page=lobby.__name__)


@routes.route("/configuracoes", methods=["GET"])
def settings():
    return render_template("configs.html", active_page=settings.__name__)


# -----------
# REST API
# -----------


@routes.route("/api/set_speed", methods=["POST"])
def set_speed():
    data = request.get_json()
    speed = data.get("speed", 0)

    simulation = get_simulation()
    simulation.speed = speed

    return jsonify({"status": "ok", "speed": simulation.speed})
