# FastAPI Migration Guide

Este documento descreve a migração do backend de Flask para FastAPI.

## O que mudou?

### Estrutura Principal
- **Novo arquivo**: `main_fastapi.py` - aplicação FastAPI completa
- **Mantido**: `main.py` - aplicação Flask original (para referência/fallback)
- **Frontend**: `vite.config.ts` atualizado para apontar para porta 8000

### Rotas Migradas
Todas as rotas foram migradas de Flask Blueprints para FastAPI APIRouters:

- ✅ `/api/simulation/*` - Gerenciamento de simulações
- ✅ `/api/portfolio/*` - Portfólio e posições
- ✅ `/api/variable-income/*` - Operações de renda variável
- ✅ `/api/fixed-income/*` - Operações de renda fixa
- ✅ `/api/session/*` - Autenticação e sessão
- ✅ `/api/user/*` - Registro e gestão de usuários
- ✅ `/api/settings` - Configurações do usuário
- ✅ `/api/statistics` - Estatísticas de performance
- ✅ `/api/set-speed` e `/api/get-simulation-state` - Controle de velocidade
- ✅ `/api/import-assets` - Importação de ativos
- ✅ `/api/stream` e `/api/update-subscription` - Realtime/SSE

### WebSocket/Realtime
- Migrado de `flask-socketio` para `python-socketio` com suporte ASGI
- Novo broker: `ws_broker_asgi.py` e `ws_handlers_asgi.py`
- Mantém compatibilidade com cliente `socket.io.js` no frontend

### DTOs (Data Transfer Objects)
- Convertidos de `dataclasses` padrão para `pydantic.dataclasses`
- Remove `slots=True` (incompatível com Pydantic v2)
- Mantém método `to_json()` para serialização

### Decorators → Dependencies
Os decorators Flask foram convertidos para FastAPI dependencies:

| Flask Decorator | FastAPI Dependency |
|----------------|-------------------|
| `@require_client_id` | `client_id: ClientID` |
| `@require_simulation` | `simulation: ActiveSimulation` |
| `@require_host` | `_: HostOnly` |

## Como Rodar

### Pré-requisitos
```bash
pip install -r requirements.txt
```

### Executar o servidor FastAPI
```bash
# Opção 1: Diretamente
python main_fastapi.py

# Opção 2: Via uvicorn
uvicorn main_fastapi:app --host 0.0.0.0 --port 8000 --reload

# Nota: Use --reload=False se estiver usando WebSocket mode
```

### Executar o frontend (Vite)
Em outro terminal:
```bash
cd frontend
npm install
npm run dev
```

O frontend estará disponível em `http://localhost:5173` e fará proxy das requisições para o backend FastAPI em `localhost:8000`.

## Documentação API

Com FastAPI, você tem acesso automático à documentação interativa:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Modo de Realtime

O aplicativo suporta dois modos de comunicação em tempo real:

### WebSocket (padrão)
- Usa `python-socketio` com backend ASGI
- Melhor para comunicação bidirecional
- Configurado em `config.toml`: `use_sse = false`

### Server-Sent Events (SSE)
- Comunicação unidirecional servidor→cliente
- Mais simples, sem necessidade de WebSocket
- Configurado em `config.toml`: `use_sse = true`

## Diferenças entre Flask e FastAPI

### Request Body
**Flask:**
```python
data = request.get_json()
ticker = data.get("ticker")
```

**FastAPI:**
```python
class MyRequest(BaseModel):
    ticker: str

def my_endpoint(payload: MyRequest):
    ticker = payload.ticker
```

### Response
**Flask:**
```python
return make_response(True, "Success", data={...})
```

**FastAPI:**
```python
return make_response(True, "Success", data={...})  # Same!
```

### Cookies
**Flask:**
```python
client_id = request.cookies.get("client_id")
```

**FastAPI:**
```python
def my_endpoint(client_id: Annotated[str | None, Cookie()] = None):
    ...
```

## Validação

FastAPI adiciona validação automática via Pydantic:

```python
class CreateSimulationRequest(BaseModel):
    start_date: str  # Validado automaticamente
    end_date: str

@router.post("/simulation/create")
def create_simulation(payload: CreateSimulationRequest):
    # payload já está validado!
    ...
```

## Testes

Execute os mesmos testes existentes, mas apontando para `localhost:8000` em vez de `localhost:5000`.

## Troubleshooting

### Erro: "No module named 'socketio'"
```bash
pip install python-socketio python-engineio
```

### Erro: "RealtimeBroker não está inicializado"
Certifique-se de que o app está sendo inicializado corretamente. O broker é criado na função `create_app()`.

### Frontend não conecta ao WebSocket
1. Verifique se `vite.config.ts` tem proxy configurado para porta 8000
2. Verifique se o backend está rodando em `http://localhost:8000`
3. Teste a conexão manualmente: `curl http://localhost:8000/api/simulation/status`

### Problemas com Database
O erro `JSONB not supported in SQLite` é do SQLAlchemy e não está relacionado à migração FastAPI. Use PostgreSQL para produção.

## Próximos Passos

1. **Testar todos os endpoints** via `/docs`
2. **Validar WebSocket** com frontend conectado
3. **Remover Flask** (opcional - se tudo funcionar)
4. **Considerar migração async** do SQLAlchemy (issue futura)

## Contribuindo

Para adicionar novos endpoints:

1. Criar models Pydantic para request/response
2. Criar rota no router apropriado
3. Usar dependencies (`ClientID`, `ActiveSimulation`, etc.)
4. Testar via `/docs`

Exemplo:
```python
from fastapi import APIRouter
from backend.fastapi_deps import ClientID
from backend.fastapi_helpers import make_response

router = APIRouter(prefix="/api", tags=["example"])

class MyRequest(BaseModel):
    name: str
    value: int

@router.post("/example")
def my_endpoint(client_id: ClientID, payload: MyRequest):
    return make_response(True, "Success", data={"name": payload.name})
```
