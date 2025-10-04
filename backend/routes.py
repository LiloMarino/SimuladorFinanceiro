from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from backend.data_loader import update_from_csv, update_from_yfinance
from backend.realtime.sse_manager import SSEManager
from backend.simulation import get_simulation

routes = Blueprint("routes", __name__)
sse = SSEManager()


# --------------------------------------------------
# 🔹 Helper padrão de resposta JSON
# --------------------------------------------------


def make_response(success: bool, message: str, data=None, status_code: int = 200):
    return (
        jsonify(
            {
                "status": "success" if success else "error",
                "message": message,
                "data": data,
            }
        ),
        status_code,
    )


# --------------------------------------------------
# REST API Endpoints
# --------------------------------------------------

# --------------------------------------------------
# 🔹 Renda Variável
# --------------------------------------------------


@routes.route("/api/renda-variavel", methods=["GET"])
def get_variable_income():
    """Retorna lista de ações (antes renderizadas em 'renda_variavel.html')."""
    try:
        simulation = get_simulation()
        stocks = simulation.get_stocks()
        return make_response(True, "Ações carregadas com sucesso.", stocks)
    except Exception as e:
        return make_response(False, f"Erro ao carregar ações: {e}", status_code=500)


@routes.route("/api/renda-variavel/<string:ativo>", methods=["GET"])
def get_variable_income_details(ativo):
    """Retorna detalhes de um ativo específico de renda variável."""
    simulation = get_simulation()
    stock = simulation.get_stock_details(ativo)
    if not stock:
        return make_response(False, "Ativo não encontrado.", status_code=404)
    return make_response(True, "Detalhes do ativo carregados.", stock)


# --------------------------------------------------
# 🔹 Renda Fixa
# --------------------------------------------------


@routes.route("/api/renda-fixa", methods=["GET"])
def get_fixed_income():
    """Retorna lista de ativos de renda fixa."""
    try:
        # Supondo que exista algo similar a simulation.get_fixed_assets()
        simulation = get_simulation()
        fixed = (
            simulation.get_fixed_assets()
            if hasattr(simulation, "get_fixed_assets")
            else []
        )
        return make_response(True, "Ativos de renda fixa carregados.", fixed)
    except Exception as e:
        return make_response(
            False, f"Erro ao carregar renda fixa: {e}", status_code=500
        )


@routes.route("/api/renda-fixa/<string:ativo>", methods=["GET"])
def get_fixed_income_details(ativo):
    """Retorna detalhes de um ativo de renda fixa."""
    try:
        simulation = get_simulation()
        details = (
            simulation.get_fixed_asset_details(ativo)
            if hasattr(simulation, "get_fixed_asset_details")
            else None
        )
        if not details:
            return make_response(False, "Ativo não encontrado.", status_code=404)
        return make_response(True, "Detalhes do ativo carregados.", details)
    except Exception as e:
        return make_response(False, f"Erro ao obter detalhes: {e}", status_code=500)


# --------------------------------------------------
# 🔹 Carteira
# --------------------------------------------------


@routes.route("/api/carteira", methods=["GET"])
def get_portfolio():
    """Retorna composição da carteira atual."""
    try:
        simulation = get_simulation()
        portfolio_data = (
            simulation.get_portfolio() if hasattr(simulation, "get_portfolio") else {}
        )
        return make_response(True, "Carteira carregada com sucesso.", portfolio_data)
    except Exception as e:
        return make_response(False, f"Erro ao carregar carteira: {e}", status_code=500)


# --------------------------------------------------
# 🔹 Importar Ativos
# --------------------------------------------------


@routes.route("/api/importar-ativos", methods=["POST"])
def import_assets():
    """Importa ativos via yfinance ou CSV."""
    data = request.get_json() or {}
    action = data.get("action")
    overwrite = data.get("overwrite", False)

    try:
        if action == "yfinance":
            ticker = data.get("ticker")
            if not ticker:
                return make_response(False, "Ticker é obrigatório.", status_code=400)
            update_from_yfinance(ticker, overwrite=overwrite)
            return make_response(True, f"Ativo '{ticker}' importado com sucesso.")

        elif action == "csv":
            ticker = data.get("ticker")
            file = request.files.get("csv_file")
            if not ticker or not file:
                return make_response(
                    False, "Ticker e arquivo CSV são obrigatórios.", status_code=400
                )
            update_from_csv(file, ticker, overwrite=overwrite)
            return make_response(True, f"Arquivo CSV '{ticker}' importado com sucesso.")

        else:
            return make_response(False, "Ação inválida.", status_code=400)

    except Exception as e:
        return make_response(False, f"Erro ao importar ativos: {e}", status_code=500)


# --------------------------------------------------
# 🔹 Estratégias / Estatísticas / Lobby / Configurações
# --------------------------------------------------


@routes.route("/api/estrategias", methods=["GET"])
def get_strategies():
    """Retorna estratégias disponíveis."""
    try:
        simulation = get_simulation()
        strategies = (
            simulation.get_strategies() if hasattr(simulation, "get_strategies") else []
        )
        return make_response(True, "Estratégias carregadas com sucesso.", strategies)
    except Exception as e:
        return make_response(
            False, f"Erro ao carregar estratégias: {e}", status_code=500
        )


@routes.route("/api/estatisticas", methods=["GET"])
def get_statistics():
    """Retorna estatísticas de desempenho."""
    try:
        simulation = get_simulation()
        stats = (
            simulation.get_statistics() if hasattr(simulation, "get_statistics") else {}
        )
        return make_response(True, "Estatísticas carregadas.", stats)
    except Exception as e:
        return make_response(
            False, f"Erro ao carregar estatísticas: {e}", status_code=500
        )


@routes.route("/api/lobby", methods=["GET"])
def get_lobby():
    """Dados do lobby ou status da simulação."""
    try:
        simulation = get_simulation()
        state = simulation.get_state() if hasattr(simulation, "get_state") else {}
        return make_response(True, "Lobby carregado com sucesso.", state)
    except Exception as e:
        return make_response(False, f"Erro ao carregar lobby: {e}", status_code=500)


@routes.route("/api/configuracoes", methods=["GET", "PUT"])
def get_or_update_settings():
    """Consulta ou atualiza configurações."""
    simulation = get_simulation()
    if request.method == "GET":
        try:
            settings = (
                simulation.get_settings() if hasattr(simulation, "get_settings") else {}
            )
            return make_response(True, "Configurações carregadas.", settings)
        except Exception as e:
            return make_response(
                False, f"Erro ao carregar configurações: {e}", status_code=500
            )
    else:
        try:
            data = request.get_json() or {}
            simulation.update_settings(data)
            return make_response(
                True,
                "Configurações atualizadas com sucesso.",
                simulation.get_settings(),
            )
        except Exception as e:
            return make_response(
                False, f"Erro ao atualizar configurações: {e}", status_code=500
            )


# --------------------------------------------------
# 🔹 Velocidade
# --------------------------------------------------


@routes.route("/api/set-speed", methods=["POST"])
def set_speed():
    data = request.get_json()
    speed = data.get("speed", 0)

    simulation = get_simulation()
    simulation.set_speed(speed)

    # Envia a atualização de velocidade via WebSocket para todos
    socketio = current_app.config.get("socketio")
    if socketio:
        socketio.emit("speed_update", {"speed": simulation.get_speed()})

    return jsonify({"speed": simulation.get_speed()})


# --------------------------------------------------
# SSE API Endpoints
# --------------------------------------------------


@routes.route("/api/stream")
def stream():
    # Cliente informa um "contexto" opcional, ex: página atual
    client_id = request.args.get("client_id", str(id(request)))
    return sse.connect(client_id)
