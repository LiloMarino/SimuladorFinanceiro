# Guia de Migração: Flask → FastAPI

## 📋 Resumo das Mudanças

Este documento descreve as mudanças realizadas na migração do backend de Flask para FastAPI.

## 🔄 Principais Alterações

### 1. Arquivo Principal
- **Antes**: `main.py` (Flask + Flask-SocketIO)
- **Depois**: `main_fastapi.py` (FastAPI + python-socketio ASGI)

### 2. Porta do Servidor
- **Antes**: `http://localhost:5000`
- **Depois**: `http://localhost:8000`

### 3. Rotas

Todos os endpoints REST foram migrados de Flask Blueprints para FastAPI Routers:

| Módulo Flask | Módulo FastAPI | Endpoints |
|--------------|----------------|-----------|
| `routes/auth.py` | `routes/fastapi_auth.py` | `/api/session/*`, `/api/user/*` |
| `routes/simulation.py` | `routes/fastapi_simulation.py` | `/api/simulation/*` |
| `routes/operation.py` | `routes/fastapi_operation.py` | `/api/variable-income/*`, `/api/fixed-income/*` |
| `routes/portfolio.py` | `routes/fastapi_portfolio.py` | `/api/portfolio/*` |
| `routes/settings.py` | `routes/fastapi_settings.py` | `/api/settings` |
| `routes/statistics.py` | `routes/fastapi_statistics.py` | `/api/statistics` |
| `routes/timespeed.py` | `routes/fastapi_timespeed.py` | `/api/set-speed`, `/api/get-simulation-state` |
| `routes/importer.py` | `routes/fastapi_importer.py` | `/api/import-assets*` |
| `routes/realtime.py` | `routes/fastapi_realtime.py` | `/api/stream`, `/api/update-subscription` |

### 4. Decorators → Dependencies

Os decorators customizados foram convertidos para dependencies do FastAPI:

| Decorator Flask | Dependency FastAPI |
|-----------------|-------------------|
| `@require_client_id` | `client_id: ClientID` |
| `@require_simulation` | `simulation: ActiveSimulation` |
| `@require_host` | `_: HostVerified` |

**Exemplo:**
```python
# Flask
@blueprint.route("/api/portfolio", methods=["GET"])
@require_client_id
@require_simulation
def get_portfolio(client_id: str, simulation: Simulation):
    ...

# FastAPI
@router.get("/api/portfolio")
async def get_portfolio(client_id: ClientID, simulation: ActiveSimulation):
    ...
```

### 5. Exceções

Exceções HTTP foram migradas de Werkzeug para FastAPI:

| Werkzeug (Flask) | FastAPI |
|------------------|---------|
| `werkzeug.exceptions.BadRequest` | `fastapi_exceptions.BadRequestError` |
| `werkzeug.exceptions.Unauthorized` | `fastapi_exceptions.UnauthorizedError` |
| `werkzeug.exceptions.Forbidden` | `fastapi_exceptions.ForbiddenError` |
| `werkzeug.exceptions.NotFound` | `fastapi_exceptions.NotFoundError` |
| `werkzeug.exceptions.Conflict` | `fastapi_exceptions.ConflictError` |
| `werkzeug.exceptions.UnprocessableEntity` | `fastapi_exceptions.UnprocessableEntityError` |

### 6. WebSocket

A implementação de WebSocket foi migrada para ASGI:

| Flask-SocketIO | python-socketio ASGI |
|----------------|---------------------|
| `flask_socketio.SocketIO` | `socketio.AsyncServer` |
| `SocketBroker` (sync) | `AsyncSocketBroker` (async-compatible) |
| `ws_handlers.py` | `async_ws_handlers.py` |

### 7. Response Format

O formato de resposta permanece o mesmo (compatibilidade mantida):

```python
# Flask
from backend.routes.helpers import make_response
return make_response(True, "Success", data={"key": "value"})

# FastAPI
from backend.routes.fastapi_helpers import make_response_data
return make_response_data(True, "Success", data={"key": "value"})
```

## 🆕 Novas Funcionalidades

### 1. Documentação Automática
FastAPI gera documentação interativa automaticamente:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### 2. Validação Automática
FastAPI usa Pydantic para validação automática de requests:
```python
class CreateSimulationRequest(BaseModel):
    start_date: str  # Validado automaticamente
    end_date: str
```

### 3. Type Hints Melhorados
Dependency injection com type hints claros:
```python
async def get_portfolio(
    client_id: ClientID,  # Auto-injected from cookie
    simulation: ActiveSimulation  # Auto-injected from manager
):
    ...
```

## 🔧 Compatibilidade

### Mantido
✅ Todas as rotas REST mantêm os mesmos endpoints  
✅ Formato de resposta JSON inalterado  
✅ WebSocket protocol compatível com cliente existente  
✅ Cookie-based authentication preservado  
✅ SQLAlchemy permanece síncrono (sem async ORM)  
✅ Simulation loop continua em thread separada  

### Alterado
⚠️ Porta do servidor: 5000 → 8000  
⚠️ Arquivo de inicialização: `main.py` → `main_fastapi.py`  
⚠️ WebSocket backend: Flask-SocketIO → python-socketio ASGI  

## 🧪 Testing

Para testar a migração:

1. **Iniciar o backend FastAPI:**
   ```bash
   python main_fastapi.py
   ```

2. **Verificar documentação:**
   ```bash
   curl http://localhost:8000/docs
   ```

3. **Testar endpoint simples:**
   ```bash
   curl http://localhost:8000/api/simulation/status
   ```

4. **Iniciar frontend:**
   ```bash
   cd frontend && npm run dev
   ```

## 📝 Notas de Desenvolvimento

### Estrutura de Arquivos
```
backend/
├── routes/
│   ├── fastapi_auth.py          # Novo (migrado)
│   ├── fastapi_simulation.py     # Novo (migrado)
│   ├── fastapi_operation.py      # Novo (migrado)
│   ├── fastapi_portfolio.py      # Novo (migrado)
│   ├── fastapi_settings.py       # Novo (migrado)
│   ├── fastapi_statistics.py     # Novo (migrado)
│   ├── fastapi_timespeed.py      # Novo (migrado)
│   ├── fastapi_importer.py       # Novo (migrado)
│   ├── fastapi_realtime.py       # Novo (migrado)
│   ├── fastapi_helpers.py        # Response helpers
│   ├── auth.py                   # Antigo (manter por ora)
│   └── ...                       # Outros módulos antigos
├── features/
│   └── realtime/
│       ├── async_ws_broker.py    # Novo (ASGI)
│       ├── async_ws_handlers.py  # Novo (ASGI)
│       ├── ws_broker.py          # Antigo (Flask)
│       └── ws_handlers.py        # Antigo (Flask)
└── core/
    ├── dependencies.py           # Novo (FastAPI deps)
    └── exceptions/
        └── fastapi_exceptions.py # Novo (FastAPI exceptions)

main_fastapi.py                   # Novo entry point
main.py                           # Antigo entry point (pode ser removido)
```

## 🚧 Próximos Passos

1. ✅ Todas as rotas migradas
2. ✅ WebSocket migrado para ASGI
3. ✅ Frontend proxy atualizado
4. ⏳ Testes manuais completos
5. ⏳ Remoção de código Flask legado (opcional)
6. ⏳ Atualização de issue #52 (OpenAPI)

## 🔗 Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [python-socketio ASGI](https://python-socketio.readthedocs.io/en/latest/server.html#asgi-mode)
- [Pydantic Documentation](https://docs.pydantic.dev/)
