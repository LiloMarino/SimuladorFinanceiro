---
sidebar_position: 2
---

# Setup do Ambiente

Configure seu ambiente de desenvolvimento para contribuir com o projeto.

## Pré-requisitos

Antes de começar, instale as seguintes ferramentas:

- **Git** — [Baixar](https://git-scm.com/)
- **uv** — [Instalar](https://docs.astral.sh/uv/getting-started/installation/) (gerencia Python e dependências automaticamente)
- **Node.js** — [Baixar](https://nodejs.org/)
- **pnpm** — Instale com `npm install -g pnpm`
- **PostgreSQL** — [Baixar](https://www.postgresql.org/)

---

## 1. Clone o Repositório

```bash
git clone https://github.com/LiloMarino/SimuladorFinanceiro.git
cd SimuladorFinanceiro
```

---

## 2. Setup do Backend (Python)

### Instalar Dependências

O projeto usa **uv** para gerenciar Python e dependências. Não é necessário criar um virtualenv manualmente — o uv faz isso automaticamente.

```bash
uv sync
```

Isso criará o virtualenv em `.venv`, instalará todas as dependências do projeto e gerará (ou validará) o lockfile `uv.lock`.

Para instalar dependências de desenvolvimento também (pytest, ruff, pyright, etc.):

```bash
uv sync --dev
```

### Configurar Variáveis de Ambiente

O projeto requer PostgreSQL. Configure a connection string via arquivo `.env`.

```bash
# Copiar arquivo de exemplo
cp example.env .env

# Editar .env com suas credenciais do PostgreSQL
nano .env  # ou use seu editor preferido
```

**Exemplo de configuração:**
```env
POSTGRES_DATABASE_URL=postgresql+psycopg://postgres:senha@localhost:5432/simulador_financeiro
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

### Opção 1 — Iniciar tudo de uma vez (recomendado)

Na raiz do projeto:

```bash
pnpm dev
```

Isso usa `concurrently` para iniciar o backend e o frontend simultaneamente em um único terminal.

:::tip Swagger Docs
Acesse `http://localhost:8000/docs` para ver a documentação interativa da API (Swagger UI).
:::

### Opção 2 — Iniciar separadamente

**Terminal 1 — Backend:**

```bash
uv run python main.py
```

O backend rodará em: **`http://localhost:8000`**

**Terminal 2 — Frontend:**

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

O projeto usa PostgreSQL. Configure o `.env` com a connection string do PostgreSQL:

1. Instale o PostgreSQL
2. Configure o `.env` com a connection string do PostgreSQL
3. Reinicie o backend - as tabelas e o banco serão criados automaticamente

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

## Próximos Passos

Agora que seu ambiente está configurado:

- [Estrutura de Pastas](./estrutura-pastas) — Entenda como o código está organizado
- [Contribuindo](./contribuindo) — Saiba como enviar suas mudanças
- [Ciclo de Desenvolvimento com BD](./ciclo-banco-dados) — Como trabalhar com o banco de dados
