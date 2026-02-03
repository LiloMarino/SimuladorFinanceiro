---
sidebar_position: 1
---

# 🔧 Setup do Ambiente

Configure seu ambiente de desenvolvimento em 5 minutos.

## Pré-requisitos

- **Git** — [Baixar](https://git-scm.com/)
- **Python 3.12+** — [Baixar](https://www.python.org/)
- **Node.js 18+** — [Baixar](https://nodejs.org/)
- **pnpm** — `npm install -g pnpm`

## Clone o Repositório

```bash
git clone https://github.com/LiloMarino/SimuladorFinanceiro.git
cd SimuladorFinanceiro
```

## Setup Backend

### 1. Criar Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. (Opcional) Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp example.env .env

# Editar .env conforme necessário
nano .env
```

## Setup Frontend

### 1. Instalar Dependências

```bash
cd frontend
pnpm install
```

### 2. Iniciar Dev Server

```bash
pnpm dev
```

Acessa: `http://localhost:5173`

## Executar Localmente

### Terminal 1 — Backend

```bash
python main.py
```

Backend rodará em `http://localhost:8000`

### Terminal 2 — Frontend

```bash
cd frontend
pnpm dev
```

Frontend rodará em `http://localhost:5173`

## Verificar Setup

Ambos os servidores rodando? ✅

- Backend: Acesse `http://localhost:8000/docs` (Swagger)
- Frontend: Acesse `http://localhost:5173`

## Próximas Lições

- [Estrutura de Pastas](./estrutura-pastas.md) — Como o código está organizado
- [Contribuindo](./contribuindo.md) — Enviar suas primeiras mudanças
