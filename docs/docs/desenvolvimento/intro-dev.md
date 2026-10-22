---
sidebar_position: 1
---

# Introdução para Devs

Bem-vindo ao guia de desenvolvimento do Simulador Financeiro!

## Sobre o Projeto

O Simulador Financeiro é uma aplicação full-stack que simula investimentos no mercado financeiro brasileiro. É um projeto open-source que combina:

- **Backend** em FastAPI, com PostgreSQL
- **Frontend** em React
- **Comunicação em tempo real** com Socket.IO
- **Dados reais** de mercado via yfinance

## Estrutura Geral

```
SimuladorFinanceiro/
├── backend/              # Python FastAPI + lógica de negócio
├── frontend/             # React + TypeScript
├── docs/                 # Documentação (este site)
├── scripts/              # Release, demonstração, OpenAPI e diagrama do banco
├── tests/                # Testes do backend (pytest)
├── main.py               # Entrypoint da aplicação
└── pyproject.toml        # Dependências Python (travadas no uv.lock)
```

## Stack Tecnológica

### Backend
- **FastAPI** — Framework web moderno
- **Uvicorn** — Servidor ASGI
- **SQLAlchemy** e **Alembic** — ORM e migrations do PostgreSQL
- **Socket.IO** — WebSockets para tempo real
- **yfinance** — Dados de mercado

### Frontend
- **React** — Biblioteca de UI
- **Shadcn** — Componentes pré-construídos
- **TypeScript** — Type safety
- **Vite** — Build tool
- **TailwindCSS** — Estilização
- **Recharts** — Gráficos

## Próximos Passos

- [Setup do Ambiente](./setup.md) — Configure sua máquina para desenvolvimento
- [Estrutura de Pastas](./estrutura-pastas.md) — Entenda como o projeto é organizado
- [Convenções do Frontend](./convencoes-frontend.md) — Como o frontend busca dados e monta formulários
- [Contribuindo](./contribuindo.md) — Aprenda como enviar suas primeiras contribuições

## Recursos Úteis

- [Repositório GitHub](https://github.com/LiloMarino/SimuladorFinanceiro)
- [Issues em Aberto](https://github.com/LiloMarino/SimuladorFinanceiro/issues) — Encontre tarefas para contribuir
- [Discussões](https://github.com/LiloMarino/SimuladorFinanceiro/discussions) — Perguntas, dúvidas e ideias