---
sidebar_position: 1
---

# 🏗️ Visão Geral da Arquitetura

Entenda como o Simulador Financeiro é estruturado.

## Arquitetura de Alto Nível

```
┌─────────────────────────────────────┐
│      React Frontend (React 19)      │
│      TypeScript + Vite + TailwindCSS│
└────────────┬────────────────────────┘
             │ HTTP + WebSocket
             │
┌────────────▼────────────────────────┐
│    FastAPI Backend (Uvicorn)        │
│    ├─ Routes (API Endpoints)        │
│    ├─ Business Logic                │
│    └─ Socket.IO (Realtime)          │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│    SQLAlchemy ORM + Database        │
│    ├─ PostgreSQL (Produção)         │
│    └─ SQLite (Desenvolvimento)      │
└─────────────────────────────────────┘
             │
┌────────────▼────────────────────────┐
│    External APIs                    │
│    └─ yfinance (Market Data)        │
└─────────────────────────────────────┘
```

## Camadas da Aplicação

### 1. Frontend (React)
- Componentes reutilizáveis
- State management com hooks
- Integração com API via fetch/axios
- WebSocket para atualizações em tempo real

### 2. API Layer (FastAPI)
- RESTful endpoints
- Validação com Pydantic
- Autenticação e autorização
- Socket.IO para comunicação bidirecional

### 3. Business Logic
- Simulação de investimentos
- Cálculo de rentabilidade
- Estratégias automatizadas
- Integração com dados externos

### 4. Data Layer (SQLAlchemy)
- Modelos ORM
- Migrations com Alembic
- Queries otimizadas
- Validações em banco

## Fluxo de Dados

### Compra de uma Ação
```
Frontend → API /operations/buy
    ↓
Validações (Saldo, Ativo, etc)
    ↓
Cria registro em banco
    ↓
Emite evento Socket.IO
    ↓
Frontend recebe atualização
    ↓
UI renderiza novo portfólio
```

## Próximas Lições

Explore as outras seções do **Desenvolvimento** para aprender mais sobre a arquitetura.
