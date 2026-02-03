---
sidebar_position: 2
---

# 📁 Estrutura de Pastas

Como o código é organizado no projeto.

## Visão Geral

```
SimuladorFinanceiro/
├── backend/                    # 🔧 Backend Python
│   ├── config/                 # Configurações
│   │   ├── env_settings.py    # Variáveis de ambiente
│   │   └── toml_settings.py   # Arquivo config.toml
│   ├── core/                   # Núcleo da aplicação
│   │   ├── database.py        # Conexão com DB
│   │   ├── logger.py          # Sistema de logs
│   │   ├── decorators/        # Decoradores úteis
│   │   ├── exceptions/        # Exceções customizadas
│   │   ├── models/            # Modelos SQLAlchemy
│   │   └── repository/        # Data access layer
│   ├── features/               # Funcionalidades
│   │   ├── fixed_income/      # Renda fixa
│   │   ├── variable_income/   # Renda variável
│   │   ├── simulation/        # Simulação
│   │   ├── strategy/          # Estratégias
│   │   └── realtime/          # WebSockets
│   ├── routes/                 # Endpoints da API
│   │   ├── auth.py            # Autenticação
│   │   ├── portfolio.py       # Portfólio
│   │   ├── operation.py       # Operações
│   │   └── ...
│   └── static/                 # Arquivos estáticos (frontend compilado)
│
├── frontend/                   # ⚛️ Frontend React
│   ├── src/
│   │   ├── components/        # Componentes React
│   │   ├── features/          # Features por domínio
│   │   ├── pages/             # Páginas
│   │   ├── shared/            # Código compartilhado
│   │   ├── types/             # TypeScript types
│   │   ├── App.tsx            # Componente raiz
│   │   └── main.tsx           # Entrypoint
│   ├── vite.config.ts         # Configuração Vite
│   └── tsconfig.json          # Configuração TypeScript
│
├── docs/                       # 📚 Documentação
│   ├── docs/                  # Markdown sources
│   ├── src/                   # Componentes da doc
│   └── docusaurus.config.ts   # Configuração
│
├── scripts/                    # 🛠️ Scripts utilitários
├── main.py                     # Entrypoint da aplicação
├── requirements.txt            # Dependências Python
├── pyproject.toml              # Configuração Poetry
└── README.md                   # Documentação principal
```

## Backend — Estrutura Detalhada

### `backend/core/models/`
Modelos de dados SQLAlchemy:
- `user.py` — Usuário
- `portfolio.py` — Portfólio do jogador
- `operation.py` — Compra/Venda de ativos

### `backend/features/`
Lógica de negócio separada por domínio:
- `variable_income/` — Operações com ações/FIIs
- `fixed_income/` — Operações com CDB/Tesouro
- `simulation/` — Engine de simulação
- `realtime/` — Eventos Socket.IO

### `backend/routes/`
Endpoints da API REST:
- `/api/auth` — Autenticação
- `/api/portfolio` — Portfólio
- `/api/market` — Dados de mercado
- `/api/operations` — Compra/Venda

## Frontend — Estrutura Detalhada

### `frontend/src/components/`
Componentes genéricos reutilizáveis

### `frontend/src/features/`
Código agrupado por feature (strategy, portfolio, etc)

### `frontend/src/types/`
Tipos TypeScript compartilhados

### `frontend/src/shared/`
- `hooks/` — Custom hooks
- `context/` — Context API
- `lib/` — Utilitários
- `components/` — Componentes básicos

## Convenções

### Backend
- **Arquivos:** `snake_case`
- **Classes:** `PascalCase`
- **Funções:** `snake_case`
- **Constantes:** `SCREAMING_SNAKE_CASE`

### Frontend
- **Arquivos:** `PascalCase` (componentes), `camelCase` (utilitários)
- **Componentes:** `PascalCase`
- **Funções:** `camelCase`
- **Hooks:** `useNomeDoHook`

## Próximas Lições

- [Contribuindo](./contribuindo.md) — Como enviar PRs
- [Arquitetura](../arquitetura/visao-geral.md) — Detalhes técnicos
