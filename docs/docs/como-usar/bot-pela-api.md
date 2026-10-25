---
sidebar_position: 12
---

# Bot pela API

Quer testar uma estratégia que não está entre as estratégias prontas do app? Escreva um **bot**: um programa na sua máquina que entra na partida como um jogador qualquer, usando as mesmas rotas HTTP e o mesmo Socket.IO que a interface usa. Ele pode ser escrito em qualquer linguagem; o exemplo desta página é em Python.

O simulador não executa o seu código: o bot roda no seu computador e só manda ordens. Por isso ele funciona com o executável, sem instalar nada no servidor e sem mexer no código do app.

## O caminho de um bot

Todas as rotas começam em `/api` e estão descritas na [referência da API](/api/simulador-financeiro). O endereço é o do host: `http://localhost:8000` no próprio computador, ou o IP da [rede local ou da VPN](./multiplayer.md#configuração-de-rede) para jogar de outra máquina.

### 1. Sessão

`POST /api/session/init` devolve o cookie `client_id`, que identifica o seu jogador. Guarde-o (em Python, uma `requests.Session` faz isso sozinha) e mande-o em toda chamada. O Socket.IO também precisa dele.

### 2. Nickname

`POST /api/user/register` com `{"nickname": "MeuBot"}`. Se o nickname já existe, a resposta é 409; para voltar a ser o mesmo jogador de uma execução anterior, use `POST /api/user/claim` com o mesmo nickname. O `claim` responde 409 enquanto a conexão da execução anterior ainda está aberta; espere alguns segundos e tente de novo.

### 3. Entrar na partida

`GET /api/session/me` traz `pending_join: true` quando há uma partida em andamento e o bot ainda não joga nela. Sem partida em andamento, as rotas de jogo (carteira, mercado, ordens) respondem 403 com "Não existe uma simulação ativa"; o bot espera e pergunta de novo. Com `pending_join`:

`POST /api/simulation/join` com `{"color": "chart-1"}`. A cor vai de `chart-1` a `chart-10`; se já tem dono, a resposta é 409 e o bot tenta a próxima. Em partida em equipes, mande também `"team"`. A partida comporta até 10 jogadores; lotada, a resposta é 423. Ao entrar, o bot recebe o saldo inicial no dia corrente, como qualquer jogador que chega depois do início (veja [Multiplayer](./multiplayer.md#entrar-com-a-partida-em-andamento)).

### 4. O tick

A partida avança um dia por vez, e cada dia é um **tick**. O bot se conecta ao Socket.IO com o mesmo cookie e assina o evento do dia:

```python
sio.emit("subscribe", {"events": ["simulation_update"]})
```

A cada `simulation_update` (que traz `current_date`, a data do novo dia) o bot lê o mercado e decide.

### 5. Ler o mercado e a carteira

| Rota | O que devolve |
| --- | --- |
| `GET /api/variable-income` | Cotação do dia de cada ativo, com setor e segmento |
| `GET /api/variable-income/{ativo}` | Detalhes do ativo e o histórico de preços (`history`) até hoje |
| `GET /api/portfolio` | Patrimônio, caixa e rentabilidade |
| `GET /api/portfolio/cash` | Só o caixa disponível |
| `GET /api/portfolio/{ativo}` | A posição no ativo: `size` (quantidade) e `reserved` (parte presa em ordens abertas) |
| `GET /api/fixed-income` | Títulos de renda fixa disponíveis, com a taxa equivalente do dia |
| `GET /api/economic-indicators` | IPCA, Selic e CDI |

### 6. Mandar ordens

| Rota | Para quê |
| --- | --- |
| `POST /api/variable-income/{ativo}/orders` | Comprar ou vender ações |
| `DELETE /api/variable-income/{ativo}/orders` com `{"order_id": "..."}` | Cancelar uma ordem aberta |
| `POST /api/fixed-income/{asset_uuid}/buy` com `{"quantity": 10}` | Comprar um título de renda fixa |

Na ordem de ações, `type` é `market` (ao preço do mercado) ou `limit` (só executa no preço combinado, informado em `limit_price`), e `action` é `buy` ou `sell`. O tamanho vem em `quantity` (quantidade de ações) ou, só na compra a mercado, em `amount` (quanto gastar, em reais). Exemplo: `{"type": "market", "action": "buy", "amount": "2000.00"}` compra R$ 2.000 em ações ao preço do mercado. A resposta traz o `order_id`, o `status` e o que a ordem executou.

## Exemplo completo: cruzamento de médias

O bot abaixo segue a estratégia pronta **Cruzamento de médias 50/200**. A média móvel é o preço médio dos últimos N dias; quando a média de 50 dias passa por cima da de 200, a alta recente ficou mais forte que a tendência longa, e o bot compra. Quando ela cruza para baixo, vende tudo do ativo. Cada compra gasta 20% do caixa.

[Baixar bot_cruzamento_medias.py](/exemplos/bot_cruzamento_medias.py). Instale as bibliotecas e rode com a partida em andamento:

```bash
pip install requests "python-socketio[client]"
python bot_cruzamento_medias.py --nickname MeuBot --tickers PETR4 VALE3 ITUB4
```

Os parâmetros `--host`, `--short`, `--long` e `--cash-pct` mudam o endereço, as janelas das médias e a fatia do caixa por compra.

```python
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
```

A decisão está na função `decide`, separada do resto: para trocar de estratégia, troque o corpo dela (e o que `buy` e `sell` mandam) e mantenha a conexão como está.

## Limitações

- **O bot fica fora do backtest.** O backtest roda sem esperar entre um dia e outro, e um bot externo não tem como acompanhar. Para comparar estratégias no backtest, use as estratégias do app.
- **Reação lenta custa dias.** A ordem do bot vale para o dia em que o simulador estiver quando ela chegar. Com o tick mais rápido que o bot, a ordem pensada para o dia analisado cai dias depois. Medido no app, com o mercado de teste (4 ativos, 2 jogadores) e o bot na mesma máquina do servidor:
  - nas velocidades ×1, ×10 e ×100, a ordem foi aceita de 6 a 9 ms depois do tick, em todos os dias testados;
  - com 80 ms de atraso simulado (rede ou cálculo pesado), ×1 e ×10 seguiram sem perder dias; a ×100, com um tick a cada 36 ms, o bot agiu em 73 de 210 dias (35%), e 72 dessas 73 ordens caíram num dia posterior ao que ele analisou.

  No mercado real o tick leva de 0,6 a 0,9 s, então um bot com rede abaixo de 100 ms acompanha a velocidade normal. O exemplo pula o dia quando ainda está decidindo o anterior, em vez de empilhar ordens atrasadas.
- **Sem proteção entre o bot e o seu computador.** O bot é um programa seu, com os mesmos acessos que você tem. Rode só código em que você confia.
