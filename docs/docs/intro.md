---
slug: /
sidebar_position: 1
---

# Introdução

**Simulador de investimentos do mercado financeiro brasileiro com modo multiplayer**

## 📌 O que é o Simulador Financeiro?

O **Simulador Financeiro** é uma aplicação web interativa inspirada em jogos de estratégia como **Capitalism Lab** e **Victoria 3**, que permite testar e competir com estratégias de investimento no **mercado financeiro brasileiro**.

Simule negociações em **renda variável** (Ações, FIIs, ETFs) e **renda fixa** (CDB, LCI, LCA, Tesouro Direto), acompanhe métricas de desempenho em tempo real e compita com outros jogadores no modo multiplayer.

<!-- Espaço reservado para screenshots e GIFs -->

## Principais Características

- **Modo Single Player e Multiplayer** — Jogue sozinho ou compita com amigos
- **Renda Variável** — Negocie ações, FIIs e ETFs com dados reais do mercado
- **Renda Fixa** — Invista em CDB, LCI, LCA e Tesouro Direto
- **Estratégias Automatizadas** — Configure algoritmos de trading personalizados
- **Dashboard Completo** — Acompanhe seu portfólio e estatísticas em tempo real
- **Controle de Tempo** — Pause, acelere ou desacelere a simulação
- **Ranking Competitivo** — Compare seu desempenho com outros jogadores
- **Executável Standalone** — Baixe e execute sem instalação

## Como Funciona

### Modo Single Player

Crie uma sessão local e teste suas estratégias de investimento sem pressão. Configure seu capital inicial, escolha seus ativos e acompanhe o desempenho do seu portfólio ao longo do tempo.

### Modo Multiplayer

1. **Host** — Crie uma sala e compartilhe o IP com seus amigos
2. **Jogadores** — Entrem na sala usando o IP fornecido
3. **Competição** — Todos começam com o mesmo capital e competem para ter o melhor retorno
4. **Vencedor** — O jogador com maior patrimônio ao final vence

### Estratégias de Investimento

- **Manual** — Tome decisões de compra e venda manualmente
- **Automática (Em desenvolvimento)** — Configure algoritmos que operam automaticamente baseados em indicadores técnicos

## 🚀 Começando

:::info
Selecione a seção **[Como Usar](./como-usar/instalacao.md)** na documentação para um guia passo a passo sobre como instalar e usar o simulador.
:::

Para desenvolvedores interessados em contribuir, consulte a seção **[Desenvolvimento](./desenvolvimento/setup.md)** para entender a arquitetura e como configurar o ambiente de desenvolvimento.

## Stack Tecnológica

### Backend
- **FastAPI** — Framework web moderno e rápido
- **Uvicorn** — Servidor ASGI de alta performance
- **SQLAlchemy** — ORM para gerenciamento de dados
- **Socket.IO** — Comunicação em tempo real via WebSockets
- **yfinance** — Dados do mercado financeiro
- **PostgreSQL / SQLite** — Banco de dados

### Frontend
- **React 19** — Biblioteca para interfaces modernas
- **TypeScript** — Type safety para JavaScript
- **Vite** — Build tool ultra-rápido
- **TailwindCSS** — Framework CSS utilitário
- **Recharts** — Biblioteca de gráficos composáveis
- **Radix UI** — Componentes acessíveis

## Licença

Este projeto está licenciado sob a [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0).
