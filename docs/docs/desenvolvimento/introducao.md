---
sidebar_position: 1
---

# 🎯 Introdução para Devs

Bem-vindo ao guia de desenvolvimento do Simulador Financeiro!

## Sobre o Projeto

O Simulador Financeiro é uma aplicação full-stack que simula investimentos no mercado financeiro brasileiro. É um projeto open-source que combina:

- **Backend robusto** com FastAPI
- **Frontend moderno** com React 19
- **Comunicação em tempo real** com Socket.IO
- **Dados reais** de mercado via yfinance

## Estrutura Geral

```
SimuladorFinanceiro/
├── backend/              # Python FastAPI + lógica de negócio
├── frontend/             # React + TypeScript
├── docs/                 # Documentação (este site)
├── scripts/              # Utilitários e scripts
├── main.py               # Entrypoint da aplicação
└── requirements.txt      # Dependências Python
```

## Stack Tecnológica

### Backend
- **FastAPI 0.128+** — Framework web moderno
- **Uvicorn** — Servidor ASGI
- **SQLAlchemy** — ORM SQL
- **Socket.IO** — WebSockets para tempo real
- **yfinance** — Dados de mercado

### Frontend
- **React 19** — UI library
- **TypeScript** — Type safety
- **Vite** — Build tool
- **TailwindCSS** — Estilização
- **Recharts** — Gráficos

## Próximos Passos

- [Setup do Ambiente](./guia-dev/setup.md) — Configure sua máquina para desenvolvimento
- [Arquitetura](./arquitetura/visao-geral.md) — Entenda como o projeto é organizado
- [Contribuindo](./guia-dev/contribuindo.md) — Aprenda como enviar suas primeiras contribuições

## Recursos Úteis

- [Repositório GitHub](https://github.com/LiloMarino/SimuladorFinanceiro)
- [Issues em Aberto](https://github.com/LiloMarino/SimuladorFinanceiro/issues) — Encontre tarefas para contribuir
- [Discussões](https://github.com/LiloMarino/SimuladorFinanceiro/discussions) — Pergunte e compartilhe ideias

## Comunidade

Dúvidas? Abra uma **Discussion** no GitHub ou contribua com melhorias! 🚀
