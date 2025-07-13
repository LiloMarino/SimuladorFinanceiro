from flask import Blueprint, redirect, render_template, url_for

routes = Blueprint("routes", __name__)


@routes.route("/", methods=["GET"])
def index():
    return redirect(url_for("routes.portfolio"))


@routes.route("/renda-variavel", methods=["GET"])
def variable_income():
    return render_template("renda_variavel.html", active_page="variable_income")


@routes.route("/renda-fixa", methods=["GET"])
def fixed_income():
    return render_template("renda_fixa.html", active_page="fixed_income")


@routes.route("/carteira", methods=["GET"])
def portfolio():
    return render_template("carteira.html", active_page="portfolio")


@routes.route("/importar-ativos", methods=["GET"])
def import_assets():
    return render_template("importar_ativos.html", active_page="import_assets")


@routes.route("/renda-variavel/<string:ativo>", methods=["GET"])
def variable_income_details(ativo):
    return render_template(
        "detalhe_renda_variavel.html", ativo=ativo, active_page="variable_income"
    )


@routes.route("/renda-fixa/<string:ativo>", methods=["GET"])
def fixed_income_details(ativo):
    return render_template(
        "detalhe_renda_fixa.html", ativo=ativo, active_page="fixed_income"
    )


@routes.route("/estrategia", methods=["GET"])
def strategies():
    return render_template("estrategias.html", active_page="strategies")


@routes.route("/estatisticas", methods=["GET"])
def statistics():
    return render_template("estatisticas.html", active_page="stats")


@routes.route("/lobby", methods=["GET"])
def lobby():
    return render_template("lobby.html", active_page="lobby")


@routes.route("/configuracoes", methods=["GET"])
def settings():
    return render_template("configs.html", active_page="settings")
