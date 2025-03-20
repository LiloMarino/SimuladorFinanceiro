import random
import threading
import time

import dash
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, dcc, html
from flask import Flask
from flask_socketio import SocketIO

# Criar a aplicação Flask
server = Flask(__name__)
app = Dash(__name__, server=server)
socketio = SocketIO(server)

# Dados iniciais
df = pd.DataFrame(columns=["Tempo", "Preço"])
tick = 0

# Layout do Dash
app.layout = html.Div(
    [
        dcc.Graph(id="live-graph"),
        dcc.Interval(
            id="interval-component", interval=500, n_intervals=0
        ),  # Atualiza a cada 0.5s
    ]
)


# Callback para atualizar o gráfico
@app.callback(
    dash.Output("live-graph", "figure"),
    [dash.Input("interval-component", "n_intervals")],
)
def update_graph(n):
    global df, tick
    tick += 1
    novo_preco = random.uniform(20, 50)  # Simula variação de preço
    novo_dado = pd.DataFrame({"Tempo": [tick], "Preço": [novo_preco]})
    df = pd.concat([df, novo_dado]).tail(100)  # Mantém os últimos 100 ticks

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Tempo"], y=df["Preço"], mode="lines", name="Preço"))
    fig.update_layout(
        title="Simulação de Tick em Tempo Real",
        xaxis_title="Tempo",
        yaxis_title="Preço",
    )

    return fig


# Thread para simular os ticks em tempo real
def gerar_ticks():
    while True:
        socketio.emit("update", {"tick": tick})
        time.sleep(0.5)


# Iniciar a thread
threading.Thread(target=gerar_ticks, daemon=True).start()

# Rodar o servidor
if __name__ == "__main__":
    socketio.run(server, debug=True)
