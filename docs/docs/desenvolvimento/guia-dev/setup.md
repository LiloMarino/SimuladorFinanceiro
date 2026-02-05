---
sidebar_position: 1
---

# Setup do Ambiente

Configure seu ambiente de desenvolvimento para contribuir com o projeto.

## Pré-requisitos

Antes de começar, instale as seguintes ferramentas:

- **Git** — [Baixar](https://git-scm.com/)
- **Python 3.12+** — [Baixar](https://www.python.org/)
- **Node.js 18+** — [Baixar](https://nodejs.org/)
- **pnpm** — Instale com `npm install -g pnpm`

### (Opcional) Ferramentas Recomendadas

- **Visual Studio Code** — Editor recomendado
- **PostgreSQL** — Para desenvolvimento com banco mais robusto (opcional, SQLite funciona por padrão)

---

## 1. Clone o Repositório

```bash
git clone https://github.com/LiloMarino/SimuladorFinanceiro.git
cd SimuladorFinanceiro
```

---

## 2. Setup do Backend (Python)

### Criar Virtual Environment

É recomendado usar um ambiente virtual para isolar as dependências do projeto.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Instalar Dependências

```bash
pip install -r requirements.txt
```

Isso instalará todas as dependências necessárias, incluindo:
- FastAPI
- Uvicorn
- SQLAlchemy
- Socket.IO
- yfinance
- E outras

### (Opcional) Configurar Variáveis de Ambiente

O projeto funciona com SQLite por padrão, mas você pode configurar PostgreSQL ou outras opções via arquivo `.env`.

```bash
# Copiar arquivo de exemplo
cp example.env .env

# Editar .env conforme necessário (opcional)
nano .env  # ou use seu editor preferido
```

**Exemplo de configuração para PostgreSQL:**
```env
DATABASE_URL=postgresql+psycopg://postgres:senha@localhost:5432/simulador_financeiro
```

---

## 3. Setup do Frontend (React + TypeScript)

### Instalar Dependências

```bash
cd frontend
pnpm install
```

Isso instalará todas as dependências do frontend, incluindo:
- React 19
- TypeScript
- Vite
- TailwindCSS
- Recharts
- E outras

---

## 4. Executar Localmente

Para rodar o projeto em modo de desenvolvimento, você precisa de **dois terminais** (um para backend, outro para frontend).

### Terminal 1 — Backend

Na raiz do projeto:

```bash
# Certifique-se de que o virtual environment está ativado
python main.py
```

O backend rodará em: **`http://localhost:8000`**

:::tip Swagger Docs
Acesse `http://localhost:8000/docs` para ver a documentação interativa da API (Swagger UI).
:::

### Terminal 2 — Frontend

Em outro terminal:

```bash
cd frontend
pnpm dev
```

O frontend rodará em: **`http://localhost:5173`**

Abra este endereço no navegador para acessar a aplicação.

---

## 5. Verificar que Tudo Está Funcionando

Se ambos os servidores estiverem rodando sem erros:

- ✅ **Backend:** Acesse `http://localhost:8000/docs` (deve mostrar o Swagger)
- ✅ **Frontend:** Acesse `http://localhost:5173` (deve mostrar a interface)
- ✅ **Conexão:** O frontend deve conseguir se comunicar com o backend

---

## Configuração Adicional

### Banco de Dados

#### SQLite (Padrão)

Por padrão, o projeto usa SQLite (`database.db` na raiz). Não requer configuração adicional.

#### PostgreSQL (Opcional)

Para melhor performance (especialmente em multiplayer), você pode usar PostgreSQL:

1. Instale o PostgreSQL
2. Crie um banco de dados:
   ```sql
   CREATE DATABASE simulador_financeiro;
   ```
3. Configure o `.env` com a connection string do PostgreSQL (veja seção 2)
4. Reinicie o backend - as tabelas serão criadas automaticamente

### Configuração TOML

Na primeira execução, um arquivo `config.toml` será criado automaticamente com configurações padrão. Você pode editá-lo para personalizar:

```toml
[database]
echo_sql = false  # Mostrar SQL queries no console

[simulation]
start_date = "2000-01-01"
end_date = "2026-01-01"
starting_cash = 10000.00
monthly_contribution = 0.0

[realtime]
use_sse = false  # true para usar SSE ao invés de WebSocket

[host]
nickname = "host"

[server]
port = 8000
provider = "lan"
preferred_vpn = null  # ou "radmin", "hamachi", "tailscale"
```

---

## Desenvolvimento em Hot Reload

Ambos backend e frontend suportam **hot reload** - suas alterações no código serão refletidas automaticamente:

- **Backend:** FastAPI recarrega automaticamente quando você altera arquivos Python
- **Frontend:** Vite recarrega automaticamente quando você altera arquivos TypeScript/React

---

## Problemas Comuns

### "Module not found"
- Certifique-se de que instalou as dependências (`pip install -r requirements.txt` e `pnpm install`)
- Verifique se o virtual environment está ativado

### "Port already in use"
- Algum processo já está usando a porta 8000 ou 5173
- No Windows: `netstat -ano | findstr :8000` e `taskkill /PID <PID> /F`
- No Linux/macOS: `lsof -ti:8000 | xargs kill -9`

### Banco de dados não conecta
- Se usando PostgreSQL, verifique se o serviço está rodando
- Verifique a connection string no `.env`
- O SQLite funciona sem configuração

---

## Próximos Passos

Agora que seu ambiente está configurado:

- [Estrutura de Pastas](./estrutura-pastas) — Entenda como o código está organizado
- [Contribuindo](./contribuindo) — Saiba como enviar suas mudanças
- [Ciclo de Desenvolvimento com BD](../ciclo-banco-dados) — Como trabalhar com o banco de dados
