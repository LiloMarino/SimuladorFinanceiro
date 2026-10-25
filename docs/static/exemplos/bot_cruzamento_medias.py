"""
Bot de exemplo do Simulador Financeiro: cruzamento de médias móveis.

Entra na partida como um jogador qualquer, pelas mesmas rotas HTTP e pelo mesmo
Socket.IO que a interface usa. A cada dia da partida compra um ativo quando a
média curta cruza a longa para cima e vende tudo dele quando cruza para baixo.

    pip install requests "python-socketio[client]"
    python bot_cruzamento_medias.py --nickname MeuBot --tickers PETR4 VALE3 ITUB4
"""

from __future__ import annotations

import argparse
import threading
import time
from decimal import ROUND_DOWN, Decimal

import requests
import socketio

# Cores da paleta de jogadores, na ordem em que o bot tenta ocupá-las
PALETTE = [f"chart-{n}" for n in range(1, 11)]


def average(values: list[float], window: int, end: int) -> float:
    """Média dos `window` valores que terminam antes de `end`."""
    return sum(values[end - window : end]) / window


def decide(closes: list[float], short: int, long: int) -> str | None:
    """
    "buy" quando a média curta passou a longa para cima hoje, "sell" quando passou
    para baixo, `None` nos demais dias. Precisa de `long + 1` fechamentos: a média
    longa de hoje e a de ontem.
    """
    if len(closes) < long + 1:
        return None
    today = average(closes, short, len(closes)) - average(closes, long, len(closes))
    yesterday = average(closes, short, len(closes) - 1) - average(
        closes, long, len(closes) - 1
    )
    if yesterday <= 0 < today:
        return "buy"
    if yesterday >= 0 > today:
        return "sell"
    return None


class Bot:
    def __init__(self, host: str, nickname: str, tickers: list[str], args):
        self.host = host.rstrip("/")
        self.nickname = nickname
        self.tickers = tickers
        self.short = args.short
        self.long = args.long
        self.cash_pct = Decimal(args.cash_pct) / 100
        # O cookie client_id identifica o jogador e é reaproveitado pelo Socket.IO
        self.http = requests.Session()
        # Fechamentos acumulados por ativo e a data do último deles
        self.closes: dict[str, list[float]] = {}
        self.last_date: dict[str, str] = {}
        # Um dia por vez: se o bot ainda decide o dia anterior, o novo é pulado
        self.busy = threading.Lock()

    def api(self, method: str, path: str, **kwargs) -> requests.Response:
        return self.http.request(method, f"{self.host}/api{path}", timeout=10, **kwargs)

    def connect(self) -> None:
        """Cookie, nickname e entrada na partida."""
        self.api("POST", "/session/init").raise_for_status()

        if not self.api("GET", "/session/me").json()["authenticated"]:
            registered = self.api(
                "POST", "/user/register", json={"nickname": self.nickname}
            )
            if registered.status_code == 409:
                # O nickname já é do bot de uma execução anterior
                registered = self.api(
                    "POST", "/user/claim", json={"nickname": self.nickname}
                )
            registered.raise_for_status()

        while True:
            if self.api("GET", "/session/me").json()["pending_join"]:
                self.join()
                return
            # Já joga na partida (execução anterior)? Sem partida, a rota recusa com 403
            if self.api("GET", "/portfolio/cash").ok:
                return
            print("Esperando uma partida em andamento...")
            time.sleep(2)

    def join(self) -> None:
        """Ocupa a primeira cor livre da paleta."""
        for color in PALETTE:
            response = self.api("POST", "/simulation/join", json={"color": color})
            if response.status_code == 409:
                continue
            response.raise_for_status()
            print(f"Dentro da partida com a cor {color}")
            return
        raise RuntimeError("Nenhuma cor livre na paleta")

    def load_history(self, ticker: str) -> None:
        """Histórico inteiro do ativo até hoje; nos dias seguintes só o fechamento novo entra."""
        history = self.api("GET", f"/variable-income/{ticker}").json()["history"]
        self.closes[ticker] = [day["close"] for day in history]
        self.last_date[ticker] = history[-1]["price_date"]

    def on_tick(self) -> None:
        if not self.busy.acquire(blocking=False):
            return
        try:
            quotes = {
                q["ticker"]: q for q in self.api("GET", "/variable-income").json()
            }
            for ticker in self.tickers:
                quote = quotes.get(ticker)
                if quote is None:
                    continue
                if ticker not in self.closes:
                    self.load_history(ticker)
                elif quote["price_date"] > self.last_date[ticker]:
                    self.closes[ticker].append(quote["close"])
                    self.last_date[ticker] = quote["price_date"]
                else:
                    continue

                signal = decide(self.closes[ticker], self.short, self.long)
                if signal == "buy":
                    self.buy(ticker)
                elif signal == "sell":
                    self.sell(ticker)
        finally:
            self.busy.release()

    def buy(self, ticker: str) -> None:
        cash = Decimal(self.api("GET", "/portfolio/cash").json()["cash"])
        amount = (cash * self.cash_pct).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        if amount <= 0:
            return
        order = {"type": "market", "action": "buy", "amount": str(amount)}
        self.send_order(ticker, order)

    def sell(self, ticker: str) -> None:
        position = self.api("GET", f"/portfolio/{ticker}").json()
        free = Decimal(position["size"]) - Decimal(position["reserved"])
        if free <= 0:
            return
        order = {"type": "market", "action": "sell", "quantity": str(free)}
        self.send_order(ticker, order)

    def send_order(self, ticker: str, order: dict) -> None:
        response = self.api("POST", f"/variable-income/{ticker}/orders", json=order)
        if response.ok:
            print(f"{order['action']} {ticker}: {response.json()}")
        else:
            print(f"Ordem recusada em {ticker}: {response.text}")

    def run(self) -> None:
        self.connect()
        sio = socketio.Client()

        @sio.event
        def connect():
            sio.emit("subscribe", {"events": ["simulation_update"]})

        @sio.on("simulation_update")
        def simulation_update(data):
            self.on_tick()

        cookie = "; ".join(f"{c.name}={c.value}" for c in self.http.cookies)
        sio.connect(self.host, headers={"Cookie": cookie})
        sio.wait()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--host", default="http://localhost:8000")
    parser.add_argument("--nickname", default="BotMedias")
    parser.add_argument("--tickers", nargs="+", default=["PETR4", "VALE3", "ITUB4"])
    parser.add_argument("--short", type=int, default=50, help="média curta, em dias")
    parser.add_argument("--long", type=int, default=200, help="média longa, em dias")
    parser.add_argument(
        "--cash-pct", type=int, default=20, help="%% do caixa por compra"
    )
    args = parser.parse_args()
    Bot(args.host, args.nickname, args.tickers, args).run()


if __name__ == "__main__":
    main()
