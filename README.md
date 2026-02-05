<div align="center">

# 📊 Simulador Financeiro

**Simulador de investimentos do mercado financeiro brasileiro com modo multiplayer**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9+-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19+-61DAFB?logo=react&logoColor=black)](https://react.dev/)

[Instalação](#-instalação) • [Como Usar](#-executando-o-projeto) • [Stack](#️-stack-tecnológica) • [Documentação](https://lilomarino.github.io/SimuladorFinanceiro/)

---

</div>

> 🇧🇷 **Projeto em Português** - Este simulador é focado no mercado financeiro brasileiro e toda a documentação está em português.

## 📌 O que é o Simulador Financeiro?

O **Simulador Financeiro** é uma aplicação web interativa inspirada em jogos de estratégia como **Capitalism Lab** e **Victoria 3**, que permite testar e competir com estratégias de investimento no **mercado financeiro brasileiro**.

Simule negociações em **renda variável** (Ações, FIIs, ETFs) e **renda fixa** (CDB, LCI, LCA, Tesouro Direto), acompanhe métricas de desempenho em tempo real e compita com outros jogadores no modo multiplayer.

<!-- Espaço reservado para screenshots e GIFs -->

### ✨ O que ele faz?

- 🎮 **Modo Single Player e Multiplayer** - Jogue sozinho ou compita com amigos
- 📈 **Renda Variável** - Negocie ações, FIIs e ETFs com dados reais do mercado
- 💰 **Renda Fixa** - Invista em CDB, LCI, LCA e Tesouro Direto
- 🤖 **Estratégias Automatizadas** - Configure algoritmos de trading personalizados
- 📊 **Dashboard Completo** - Acompanhe seu portfólio e estatísticas em tempo real
- ⏱️ **Controle de Tempo** - Pause, acelere ou desacelere a simulação
- 🎯 **Ranking Competitivo** - Compare seu desempenho com outros jogadores


## 🎮 Como Funciona

### Modo Single Player
Crie uma sessão local e teste suas estratégias de investimento sem pressão. Configure seu capital inicial, escolha seus ativos e acompanhe o desempenho do seu portfólio ao longo do tempo.

### Modo Multiplayer
1. **Host** - Crie uma sala e compartilhe o IP com seus amigos
2. **Jogadores** - Entrem na sala usando o IP fornecido
3. **Competição** - Todos começam com o mesmo capital e competem para ter o melhor retorno
4. **Vencedor** - O jogador com maior patrimônio ao final vence

### Estratégias de Investimento
- **Manual** - Tome decisões de compra e venda manualmente
- **Automática (Em desenvolvimento)** - Configure algoritmos que operam automaticamente baseados em indicadores técnicos


## 📥 Instalação

### Instalação via Executável Standalone

Baixe o executável disponível em [Releases](../../releases), escolha o arquivo conforme seu sistema operacional e execute-o diretamente. O navegador abrirá automaticamente em `http://localhost:8000`.

### Instalação a partir do Código-Fonte
Clone o repositório e instale as dependências:

```bash
git clone https://github.com/LiloMarino/SimuladorFinanceiro.git
cd SimuladorFinanceiro
```

**Backend (Python 3.12+)**
```bash
pip install -r requirements.txt
```

**Frontend (Node.js + pnpm)**
```bash
cd frontend
pnpm install
```

**Configuração (Opcional)**
```bash
# Copie o arquivo de exemplo de variáveis de ambiente
cp example.env .env

# Edite .env com suas configurações (banco de dados, etc.)
```

> [!IMPORTANT]
> O projeto funciona com SQLite. Porém é recomendado usar PostgreSQL e para isso é necessário configurar as variáveis de ambiente no arquivo `.env`.

## Executando o Projeto Localmente

### Modo Desenvolvimento

**Backend:**
```bash
python main.py
```

**Frontend (em outro terminal):**
```bash
cd frontend
pnpm dev
```

Acesse: `http://localhost:5173` (frontend dev) ou `http://localhost:8000` (backend direto)

### Modo Produção (Compilado)

```bash
make build
./dist/SimuladorFinanceiro
```

Acesse: `http://localhost:8000`

## 🛠️ Stack Tecnológica

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno e rápido
- **[Uvicorn](https://www.uvicorn.org/)** - Servidor ASGI de alta performance
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM para gerenciamento de dados
- **[Socket.IO](https://socket.io/)** - Comunicação em tempo real via WebSockets
- **[yfinance](https://pypi.org/project/yfinance/)** - Dados do mercado financeiro
- **PostgreSQL / SQLite** - Banco de dados (PostgreSQL preferencial, SQLite para fallback)

### Frontend
- **[React 19](https://react.dev/)** - Biblioteca para interfaces modernas
- **[TypeScript](https://www.typescriptlang.org/)** - Type safety para JavaScript
- **[Vite](https://vitejs.dev/)** - Build tool ultra-rápido
- **[TailwindCSS](https://tailwindcss.com/)** - Framework CSS utilitário
- **[Recharts](https://recharts.org/)** - Biblioteca de gráficos composáveis
- **[Lightweight Charts](https://tradingview.github.io/lightweight-charts/)** - Gráficos financeiros profissionais
- **[Radix UI](https://www.radix-ui.com/)** - Componentes acessíveis e não-estilizados
- **[React Query](https://tanstack.com/query/latest)** - Gerenciamento de estado assíncrono
- **[React Router](https://reactrouter.com/)** - Roteamento declarativo

### Ferramentas de Build
- **[PyInstaller](https://pyinstaller.org/)** - Empacotamento do Python em executável
- **[Make](https://www.gnu.org/software/make/)** - Automação de build
  
## 🤝 Contribuindo

Contribuições são bem-vindas! Veja a [documentação completa](https://lilomarino.github.io/SimuladorFinanceiro/) para guias de desenvolvimento.

**Formas de contribuir:**
- 🐛 Reportar bugs via [Issues](../../issues)
- 💡 Sugerir novas funcionalidades via [Discussions](../../discussions)
- 🔧 Enviar pull requests
- 📖 Melhorar a documentação

---

## 📜 Licença

Este projeto está licenciado sob a [GNU General Public License v3.0](LICENSE).

Você é livre para usar, modificar e distribuir este software, desde que mantenha a mesma licença e atribua os devidos créditos.

---

<div align="center">

**Desenvolvido por [Murilo Marino](https://github.com/LiloMarino) • [⭐ Dê uma estrela no projeto!](../../stargazers)**

</div>
