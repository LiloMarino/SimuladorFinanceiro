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
[simulation]
start_date = "2000-01-01"
end_date = "2026-01-01"
starting_cash = 10000.00
monthly_contribution = 0.0
price_impact_enabled = false  # Padrão do lobby para o impacto de preço das ordens
price_impact_k = 0.02         # Intensidade do impacto
price_impact_decay_days = 20  # Pregões até o preço voltar ao histórico

[host]
nickname = "host"

[server]
port = 8000
provider = "lan"
preferred_vpn = null  # ou "radmin", "hamachi", "tailscale"

[logging]
logs_path = "logs"

[debug]
enabled = false  # true liga o modo debug (veja abaixo)
sql = false      # com o debug ligado, grava o SQL no database.log
```

O proxy do `pnpm dev` do frontend (`/api` e `/socket.io`) segue o `[server] port` deste arquivo, ou 8000 quando ele não existe. Ao mudar a porta, reinicie o `pnpm dev`.

O que cada arquivo de `logs_path` guarda e o que aparece no terminal está em [Logs](./logs.md).

### Modo debug

O modo debug serve para investigar lentidão e comportamento estranho na máquina de quem joga. Ele é decidido **ao subir o servidor**: não existe botão na interface, e para mudá-lo é preciso fechar e abrir o app de novo. Vem desligado, tanto em desenvolvimento quanto no executável. Para ligar, use uma das formas:

- `enabled = true` na seção `[debug]` do `config.toml`;
- `--debug` na linha de comando, que liga mesmo com o `config.toml` desligado:

  ```bash
  uv run python main.py --debug
  # ou, no executável
  SimuladorFinanceiro.exe --debug
  ```

Ligado, o modo debug:

- grava o `DEBUG` do código do app (ordem recebida e casada, dia simulado, importação por ticker, cada requisição HTTP) no `app.log` e nos arquivos por área (`simulation.log`, `realtime.log`, `import.log`). As bibliotecas (`sqlalchemy`, `engineio`, `socketio`, `urllib3`, `asyncio`) continuam em `WARNING`, o `error.log` segue só com `ERROR` e `CRITICAL`, e o terminal não muda;
- com `sql = true`, grava as consultas SQL no `database.log` (e só nele);
- mostra as ferramentas do TanStack Query (o botão no canto da tela) e libera os logs `debug` e `log` do console do navegador, inclusive no executável. Desligado, o front se comporta igual em desenvolvimento e no executável;
- libera o painel **Desempenho** (só para o host), que mede onde o tempo vai na partida. Veja [Investigando lentidão](./investigando-lentidao.md).

O servidor informa o modo em `GET /api/settings` (campo `debug`, somente leitura).


---

## Próximos Passos

Agora que seu ambiente está configurado:

- [Estrutura de Pastas](./estrutura-pastas) — Entenda como o código está organizado
- [Contribuindo](./contribuindo) — Saiba como enviar suas mudanças
- [Ciclo de Desenvolvimento com BD](./ciclo-banco-dados) — Como trabalhar com o banco de dados
