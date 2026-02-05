---
sidebar_position: 4
---

# Diretrizes Async vs Sync

Este projeto **adota explicitamente um modelo híbrido (sync + async)**. Esta página documenta as convenções e padrões para trabalhar com código síncrono e assíncrono.

## Filosofia do Projeto

O objetivo é **conter o código assíncrono na camada de transporte** e evitar que ele se propague para o core (domínio e engine de simulação).

:::info Princípio Chave
**O domínio não conhece `asyncio`, event loop ou `await`.**  
Async é um detalhe da camada de transporte, não da regra de negócio.
:::

---

## Convenções Adotadas

### Domínio e Engine (Síncrono)

A lógica central da simulação — `backend/features/simulation/*`, `Simulation`, `SimulationEngine`, `UserManager` e a maior parte dos repositórios/DAO — **deve permanecer síncrona** (`def`).

**Por quê?**
- Essas camadas executam cálculos, regras de negócio e acesso síncrono a dados
- Podem rodar em threads dedicadas
- Não precisam de I/O assíncrono
- Código mais simples e fácil de manter

**Exemplo:**
```python
class SimulationEngine:
    def calculate_portfolio_value(self, user_id: int) -> float:
        # Lógica síncrona
        positions = self.repository.get_positions(user_id)
        return sum(p.quantity * p.current_price for p in positions)
```

---

### Loop da Simulação (Thread Dedicada)

A `SimulationLoopController` roda em uma **thread separada** e deve usar `time.sleep()` e mecanismos de sincronização de thread (`threading.Lock`).

**❌ NÃO transforme o loop em coroutine**, pois isso forçaria a migração do core para async.

**Exemplo:**
```python
import threading
import time

class SimulationLoopController:
    def __init__(self):
        self.running = False
        self.lock = threading.Lock()
        
    def run(self):
        """Roda em thread separada"""
        while self.running:
            with self.lock:
                self.engine.tick()  # Método síncrono
            
            time.sleep(self.tick_interval)  # Síncrono, não asyncio.sleep
```

**Iniciando a thread:**
```python
thread = threading.Thread(target=controller.run, daemon=True)
thread.start()
```

---

### Camada de Transporte (Async)

Web e WebSocket (FastAPI/ASGI, `socketio.AsyncServer`, handlers, middlewares) **são assíncronos por natureza** e devem permanecer `async def`.

**Por quê?**
- FastAPI é construído sobre ASGI (assíncrono)
- WebSocket requer async
- Permite alta concorrência para múltiplos clientes

**Exemplo:**
```python
@router.get("/portfolio/{user_id}")
async def get_portfolio(user_id: int):
    # Endpoint assíncrono
    portfolio = await asyncio.to_thread(
        simulation_engine.get_portfolio,  # Método síncrono
        user_id
    )
    return portfolio
```

:::tip
Use `asyncio.to_thread()` para chamar código síncrono de forma assíncrona, evitando bloqueio do event loop.
:::

---

### `notify()` - Fire and Forget

A função `notify(event, payload, to=None)` do broker realtime é **síncrona e fire-and-forget**.

**Por quê?**
Isso permite que o domínio chame notificações sem depender de `async` ou `await`.

**Exemplo:**
```python
# No domínio (síncrono)
class SimulationEngine:
    def execute_trade(self, order):
        # Lógica de execução
        trade = self.match_order(order)
        
        # Notificar sem async
        notify("trade_executed", {
            "trade_id": trade.id,
            "order_id": order.id
        })
```

---

### Entrega Assíncrona Interna

A implementação do broker é responsável por **agendar a entrega dos eventos no event loop**, sem bloquear a thread chamadora.

**Como fazer:**
Use `asyncio.run_coroutine_threadsafe()` ou mecanismos equivalentes do transporte.

**Exemplo de implementação no broker:**
```python
class SocketBroker:
    def notify(self, event: str, payload: dict, to: str | None = None):
        """Método síncrono fire-and-forget"""
        # Agenda a coroutine no event loop sem bloquear
        asyncio.run_coroutine_threadsafe(
            self._async_notify(event, payload, to),
            self.loop
        )
    
    async def _async_notify(self, event: str, payload: dict, to: str | None):
        """Método assíncrono interno"""
        if to:
            await self.sio.emit(event, payload, to=to)
        else:
            await self.sio.emit(event, payload)
```

---

## Padrões de Integração

### Chamando Código Síncrono de Async

Use `asyncio.to_thread()` para rodar código síncrono bloqueante sem bloquear o event loop:

```python
@router.post("/start-simulation")
async def start_simulation(config: SimulationConfig):
    # Executa método síncrono em thread separada
    simulation = await asyncio.to_thread(
        simulation_manager.create_simulation,
        config
    )
    return {"simulation_id": simulation.id}
```

:::warning
Nunca chame código bloqueante síncrono diretamente em um endpoint async sem `to_thread()`. Isso bloqueará o event loop!
:::

---

### Chamando Código Async de Sync

Use `asyncio.run_coroutine_threadsafe()` para agendar coroutines de código síncrono:

```python
# Domínio síncrono precisa notificar via broker async
def execute_trade(self, order):
    trade = self.match_order(order)
    
    # Agenda notificação no event loop
    asyncio.run_coroutine_threadsafe(
        broker.async_notify("trade", trade.dict()),
        broker.loop
    )
```

Ou simplesmente use o método `notify()` fire-and-forget do broker, que já faz isso internamente.

---

## Diagramas de Arquitetura

### Fluxo Sync-Async

```
┌─────────────────────────────────────────────────────────────┐
│                    Camada de Transporte (Async)             │
│                                                               │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  FastAPI    │    │  WebSocket   │    │  Middlewares │  │
│  │  Endpoints  │    │  Handlers    │    │              │  │
│  └──────┬──────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                  │                    │           │
└─────────┼──────────────────┼────────────────────┼───────────┘
          │                  │                    │
          │ asyncio.to_thread()                  │
          ▼                  │                    ▼
┌─────────────────────────────────────────────────────────────┐
│                   Domínio e Engine (Sync)                    │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Simulation  │  │  Engine      │  │  Repository  │      │
│  │  Manager     │  │              │  │  (DAO)       │      │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘      │
│         │                  │                                 │
│         │ notify()         │ threading                       │
│         ▼                  ▼                                 │
│  ┌──────────────────────────────┐                           │
│  │  Realtime Broker (notify)    │                           │
│  └────────────┬─────────────────┘                           │
│               │ run_coroutine_threadsafe()                   │
└───────────────┼──────────────────────────────────────────────┘
                │
                ▼
        Event Loop (async emit)
```

---

## Exemplos Completos

### Exemplo 1: Endpoint que Executa Lógica Síncrona

```python
# backend/routes/operations.py
@router.post("/buy")
async def buy_asset(order: OrderCreate, user_id: int = Depends(get_current_user)):
    # Executa lógica síncrona em thread separada
    result = await asyncio.to_thread(
        broker.execute_buy_order,  # Método síncrono
        user_id,
        order
    )
    return result
```

### Exemplo 2: Domínio Notificando via Broker

```python
# backend/features/variable_income/broker.py
class VariableIncomeBroker:
    def execute_buy_order(self, user_id: int, order: Order):
        """Método síncrono do domínio"""
        # Lógica de execução
        trade = self.match_engine.match(order)
        
        # Notifica todos os clientes (fire-and-forget)
        notify("trade_executed", {
            "user_id": user_id,
            "trade": trade.dict()
        })
        
        return trade
```

### Exemplo 3: Loop de Simulação em Thread

```python
# backend/features/simulation/simulation_loop.py
import threading
import time

class SimulationLoop:
    def __init__(self, engine):
        self.engine = engine
        self.running = False
        self.thread = None
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
    def _run(self):
        while self.running:
            # Lógica síncrona
            self.engine.tick()
            
            # Sleep síncrono
            time.sleep(1.0 / self.engine.speed)
            
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
```

---

## Vantagens desta Arquitetura

✅ **Simplicidade do domínio** - Lógica de negócio mais fácil de entender e manter

✅ **Testabilidade** - Código síncrono é mais fácil de testar

✅ **Performance** - Threads para CPU-bound, async para I/O-bound

✅ **Isolamento** - Mudanças na camada de transporte não afetam o domínio

✅ **Flexibilidade** - Fácil trocar entre SSE e WebSocket

---

## Regra de Ouro

> **O domínio não conhece `asyncio`, event loop ou `await`.**  
> Async é um detalhe da camada de transporte, não da regra de negócio.

Se você se pegar adicionando `async/await` em código de domínio, pare e reconsidere a arquitetura.

---

## Próximos Passos

- [Estrutura de Pastas](./guia-dev/estrutura-pastas) — Entenda onde cada tipo de código vive
- [Contribuindo](./guia-dev/contribuindo) — Como enviar suas mudanças
