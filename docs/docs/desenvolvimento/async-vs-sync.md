---
sidebar_position: 5
---

# Diretrizes Async vs Sync

Este projeto adota **deliberadamente** um modelo híbrido (**sync + async**).

A arquitetura é construída de forma que:
- o **core da simulação e do domínio seja estritamente síncrono**
- o **código assíncrono fique restrito à camada de transporte** (ASGI, WebSocket, Socket.IO)

Este documento define as **regras oficiais** para essa separação, evitando o vazamento de `async/await` para o domínio e garantindo integração segura com o event loop.

:::note Decisão Arquitetural (ADR)
Este documento registra uma **decisão arquitetural explícita** do projeto.

Alterar o modelo sync/async descrito aqui **impacta diretamente o determinismo, o controle de estado e o modelo de execução da simulação** e **não deve ser feito sem reavaliar toda a arquitetura e seus trade-offs**.
:::

## Filosofia do Projeto

O objetivo é **conter o código assíncrono na camada de transporte** e impedir que conceitos como `await`, `asyncio` ou event loop contaminem o domínio.

:::info Princípio Chave
**O domínio não conhece `asyncio`, event loop ou `await`.**  
Async é um detalhe de infraestrutura, não de regra de negócio.
:::

---

## Convenções por Camada

### Domínio e Engine (Síncrono)

A lógica central da simulação — `backend/features/simulation/*`, `Simulation`, `SimulationEngine`, `UserManager` e repositórios/DAO — **permanece intencionalmente síncrona** (`def`).

**Motivos:**
- Executa regras de negócio e cálculos determinísticos
- Possui estado mutável controlado
- Não depende de I/O assíncrono
- É mais simples de testar, depurar e raciocinar
- Pode rodar de forma previsível em uma thread dedicada

**Exemplo:**
```python
class SimulationEngine:
    def calculate_portfolio_value(self, user_id: int) -> float:
        positions = self.repository.get_positions(user_id)
        return sum(p.quantity * p.current_price for p in positions)
````

---

### Loop da Simulação (Thread Dedicada)

O loop de simulação roda em **uma thread própria**, separada do event loop assíncrono da aplicação.

Essa decisão **não é uma preferência estilística**, mas uma consequência direta do modelo de execução da simulação.

A simulação é um processo contínuo que possui:

* um `while` controlando explicitamente o ciclo de vida
* execução sequencial de `next_tick()`
* controle manual de tempo (`sleep`)
* sincronização explícita de estado (`lock`)
* necessidade de previsibilidade e determinismo

Esse tipo de execução **é inerentemente síncrono**.

Uma thread Python executa código de forma **sequencial e bloqueante**.
Portanto, o código que roda dentro dela **deve ser síncrono** para manter simplicidade e previsibilidade.

Tornar esse loop assíncrono exigiria:

* transformar `next_tick()` em `async`
* propagar `async/await` por todo o core
* trocar `threading.Lock` por `asyncio.Lock`
* introduzir conversões constantes entre sync ↔ async

Tudo isso **aumentaria a complexidade**, sem trazer ganhos reais para esse tipo de simulação.

---

#### Estrutura do Loop

```python
import threading
import time

class SimulationLoopController:
    def __init__(self, engine):
        self.engine = engine
        self.running = False
        self.lock = threading.Lock()
        self.tick_interval = 1.0

    def run(self):
        """Executa em thread dedicada"""
        while self.running:
            with self.lock:
                self.engine.next_tick()  # Código síncrono
            time.sleep(self.tick_interval)
```

Esse modelo oferece:

* execução previsível e determinística do `tick`
* isolamento total do core em relação ao event loop async
* uso direto de primitivas de sincronização (`threading.Lock`)
* controle explícito de tempo sem dependência de `asyncio`
* menor custo cognitivo e arquitetural

---

#### Inicialização da Thread

```python
thread = threading.Thread(
    target=controller.run,
    daemon=True,
)
thread.start()
```

---

### Camada de Transporte (Async)

FastAPI, ASGI, WebSocket e Socket.IO **são assíncronos por definição**.

Nessa camada, o uso de `async` **é obrigatório**, mas **não deve vazar para o core**.

Quando necessário, o transporte faz a ponte chamando código síncrono de forma segura.

**Exemplo:**

```python
@router.get("/portfolio/{user_id}")
async def get_portfolio(user_id: int):
    portfolio = await asyncio.to_thread(
        simulation_engine.get_portfolio,  # método síncrono
        user_id
    )
    return portfolio
```

---

## Pontes entre Sync e Async (Regra de Ouro)

### Async → Sync (event loop chamando código bloqueante)

✔ **Use `asyncio.to_thread()`**

```python
result = await asyncio.to_thread(sync_function, arg1, arg2)
```

**Quando usar:**

* Endpoint FastAPI chamando domínio
* Handler WebSocket chamando engine
* Qualquer código async chamando algo bloqueante

---

### Sync → Async (thread chamando coroutine)

✔ **Use `asyncio.run_coroutine_threadsafe()`**

```python
asyncio.run_coroutine_threadsafe(coro(), loop)
```

**Quando usar:**

* Loop de simulação notificando WebSocket
* Core disparando eventos realtime
* Código síncrono que precisa interagir com async

---

## `notify()` — Fire and Forget (Padrão Oficial)

O broker realtime expõe um método **síncrono**, propositalmente:

```python
def notify(event, payload, to=None) -> None
```

**Por quê?**

* O core é síncrono
* O core não deve depender de `await`
* Notificação é efeito colateral, não fluxo principal

---

### Implementação Correta do Broker

A responsabilidade de fazer a ponte **sync → async** é **exclusivamente do broker**.

```python
class SocketBroker:
    def notify(
        self,
        event: str,
        payload: dict,
        to: str | None = None,
    ) -> None:
        if self._loop is None:
            raise RuntimeError("Event loop não está vinculado ao SocketBroker")

        asyncio.run_coroutine_threadsafe(
            self._async_notify(event, payload, to),
            self._loop,
        )

    async def _async_notify(
        self,
        event: str,
        payload: dict,
        to: str | None,
    ):
        if to is not None:
            await self.sio.emit(event, payload, to=to)
        else:
            await self.sio.emit(event, payload)
```

---

### Exemplo Real (Core Síncrono)

```python
class SimulationEngine:
    def execute_trade(self, order):
        trade = self.match_order(order)

        # Fire-and-forget
        self.broker.notify(
            event="trade_executed",
            payload={
                "trade_id": trade.id,
                "order_id": order.id,
            },
        )
```

---

## Diagrama Final de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                Camada de Transporte (Async)                 │
│                                                             │
│  FastAPI / WebSocket / Socket.IO                            │
│                                                             │
│  async → sync  → asyncio.to_thread()                        │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│                 Domínio e Engine (Sync)                     │
│                                                             │
│  SimulationEngine / Loop / Core                             │
│                                                             │
│  sync → async → notify()                                    │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│               Realtime Broker (Async Bridge)                │
│                                                             │
│  asyncio.run_coroutine_threadsafe()                         │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
          Event Loop (emit WebSocket)
```
