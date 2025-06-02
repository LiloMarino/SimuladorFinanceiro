# 📊 Simulador Financeiro  

## 📌 Visão Geral  
O **Simulador Financeiro** é uma aplicação interativa inspirada em jogos RTS como **Capitalism Lab e Victoria 3**, que permite testar estratégias de investimento no **mercado financeiro brasileiro**. O simulador inclui **renda fixa (CDB, LCI, LCA, Tesouro Direto)** e **renda variável (Ações, FIIs, ETFs)**, além de eventos econômicos dinâmicos, métricas de desempenho e suporte a múltiplas fontes de dados.  

O objetivo é oferecer um ambiente dinâmico para experimentação de estratégias de compra e venda de ativos, seja de forma automática ou manual.  

## 🎮 Modos de Jogo  

### 1️⃣ **Modo Automático** 📈  
- O tempo avança automaticamente, como em um RTS.  
- As compras e vendas são executadas conforme uma **estratégia de negociação programada**.  
- O usuário pode configurar e testar diferentes **algoritmos de investimento**.  

### 2️⃣ **Modo Manual** 🏦  
- O jogador pode **emitir ordens de compra e venda manualmente**.  
- O mercado segue em tempo real, e o usuário decide **quando intervir**.  
- O tempo pode ser pausado ou acelerado (**1x, 2x, 4x, 10x**).  

### 3️⃣ **Modo Multiplayer** 🌐  
- Permite **vários jogadores** competindo simultaneamente.  
- O jogo sincroniza eventos econômicos e tempo de simulação para todos os participantes.  
- O jogador com o maior patrimônio ao final vence.  

## 🔥 Funcionalidades Principais  

✅ **Simulação de negociações** (Ações, FIIs, ETFs) em tempo real.  
✅ **Investimentos em renda fixa** (CDB, LCI, LCA, Tesouro Direto).  
✅ **Fluxo de caixa mensal** (simulação de salário ou renda fixa recorrente).  
✅ **Análise de desempenho**: Retorno, drawdown, índice de Sharpe, etc.  
✅ **Eventos econômicos dinâmicos**: Crises, mudanças nos juros e inflação.  
✅ **Gráficos interativos** em **Plotly + Dash** para acompanhar a evolução do portfólio.  
✅ **Interface Web personalizada** via **Flask + Dash + CSS**.  
✅ **Suporte a múltiplas fontes de dados** (Yahoo Finance, MySQL, SQLite).  
✅ **Modo Multiplayer** com servidor cliente-servidor via **WebSockets**.  
✅ **Atualizações em tempo real** simulando ticks do mercado.  
✅ **Empacotamento como executável (.exe)** para facilitar a distribuição.  

## 🛠️ Tecnologias Utilizadas  

- **[Backtrader](https://www.backtrader.com/)** → Motor de backtesting e simulação.  
- **[Flask](https://flask.palletsprojects.com/)** → Backend da aplicação.  
- **[Dash](https://dash.plotly.com/)** → Framework para interface gráfica interativa.  
- **[Plotly](https://plotly.com/python/)** → Gráficos dinâmicos para acompanhamento do portfólio.  
- **[yfinance](https://pypi.org/project/yfinance/)** → Dados do mercado financeiro.  
- **[SQLAlchemy](https://www.sqlalchemy.org/)** → ORM para banco de dados.  
- **[Alembic](https://alembic.sqlalchemy.org/)** → Controle de versões do banco de dados.  
- **Banco de Dados** → **MySQL e SQLite** para armazenamento de históricos e portfólio.  
- **WebSockets** → Comunicação em tempo real para atualização de gráficos e multiplayer.  
- **PyInstaller** → Empacotamento da aplicação como executável (.exe).  

## 🔧 Configuração e Instalação  

1. **Instale o Python 3.9+**  
2. **Instale as dependências**:  
   ```bash
   pip install -r requirements.txt
   ```  
3. **Configure as fontes de dados**:  
   - Dados de ações e FIIs via **Yahoo Finance** ou **API da B3**.  
   - Dados de renda fixa simulados conforme o CDI e IPCA.  

4. **Configurar banco de dados e Alembic**:  
   - Para MySQL, edite o arquivo `alembic.ini`:  
     ```ini
     sqlalchemy.url = mysql+mysqlconnector://usuario:senha@localhost/seu_banco
     ```
   - Para SQLite, use:  
     ```ini
     sqlalchemy.url = sqlite:///banco.db
     ```
   - Crie as tabelas do banco:  
     ```bash
     alembic upgrade head
     ```

---

## 📁 Estrutura do Projeto  

```plaintext
/simulador-financeiro
├── backend/               # Lógica do servidor Flask
│   ├── models.py          # Modelos do SQLAlchemy
│   ├── database.py        # Configuração do banco de dados
│   ├── routes.py          # Rotas da aplicação (views)
│   ├── websocket.py       # Comunicação em tempo real
│   ├── strategies/        # Estratégias de negociação automatizadas
│   ├── data_loader.py     # Manipulação de dados históricos
│   ├── templates/         # Templates HTML (Jinja2)
│   │   ├── base.html      # Template base para reutilização
│   │   ├── index.html     # Página inicial
│   │   ├── dashboard.html # Painel de investimentos
│   │   ├── trade.html     # Tela de negociação manual
│   │   └── multiplayer.html # Tela do modo multiplayer
│   ├── static/            # Arquivos estáticos (CSS, JS, imagens)
│   │   ├── css/
│   │   │   ├── style.css  # Estilos personalizados
│   │   ├── js/
│   │   │   ├── app.js     # Scripts da aplicação
│   │   ├── img/           # Imagens e ícones
│   └── __init__.py
│
├── migrations/            # Migrações do Alembic
│
├── main.py                # Ponto de entrada da aplicação Flask
├── requirements.txt       # Lista de dependências
├── README.md              # Documentação
└── server.py              # Servidor do modo multiplayer
```

## 🔄 Fluxo de Desenvolvimento: MySQL Workbench + SQLAlchemy + Alembic

Este projeto adota um ciclo de desenvolvimento que combina a praticidade do **MySQL Workbench** com o poder de versionamento do **Alembic** e a portabilidade do **SQLAlchemy**. Isso permite que a aplicação funcione tanto com **MySQL**, **SQLite** ou outros bancos compatíveis com o SQLAlchemy.

### 📌 Etapas do Fluxo

```text
1️⃣ Modela visualmente no MySQL Workbench (.mwb)
⬇️
2️⃣ Atualiza o banco MySQL (via Forward Engineering)
⬇️
3️⃣ Gera o ORM automaticamente com sqlacodegen
⬇️
4️⃣ Usa Alembic para rastrear e controlar as mudanças
⬇️
5️⃣ Aplica migrações em múltiplos bancos (MySQL, SQLite, etc)
🔁
```

### 🧰 Comandos úteis

#### 1. Gerar modelos ORM com `sqlacodegen`

```bash
sqlacodegen mysql+pymysql://<usuario>:<senha>@<localhost>/<nomedobanco> > backend/models.py
```

#### 2. Inicializar Alembic (uma vez apenas)

```bash
alembic init migrations
```

Isso criará uma pasta `/migrations` com a estrutura de controle de versões.

#### 3. Configurar o banco no `alembic.ini`

No arquivo `alembic.ini`, altere a string de conexão:

```ini
sqlalchemy.url = mysql+pymysql://<usuario>:<senha>@<localhost>/<nomedobanco>
```

Ou defina dinamicamente em `backend/database.py` (mais flexível).

#### 4. Gerar migração automaticamente com base nas alterações do ORM

```bash
alembic revision --autogenerate -m "Nova versão do modelo"
```

#### 5. Aplicar a migração ao banco configurado

```bash
alembic upgrade head
```

## 🚀 Como Executar  

1. Clone o repositório:  
   ```bash
   git clone https://github.com/seu-repositorio/simulador-financeiro.git
   cd simulador-financeiro
   ```  

2. Instale as dependências:  
   ```bash
   pip install -r requirements.txt
   ```  

3. Inicie o backend Flask:  
   ```bash
   python main.py
   ```  

4. Inicie a interface gráfica Dash:  
   ```bash
   python frontend/app.py
   ```  

5. Para ativar o **modo multiplayer**, inicie o servidor WebSockets antes de conectar os clientes:  
   ```bash
   python server.py
   ```  

## Estrutura

| Necessidade                      | Ferramenta recomendada                   |
| -------------------------------- | ---------------------------------------- |
| Atualizar gráfico a cada 2s      | Dash + Plotly                            |
| Mostrar preço em tempo real      | WebSocket ou AJAX (JS)                   |
| Dashboard interativo com filtros | Dash (com ou sem Plotly)                 |
| Vários usuários sincronizados    | WebSocket com servidor (ex: `socket.io`) |
| Site bonito com HTML pronto      | DeepSite + Jinja2                        |


```plaintext
📦 backend/
│
├── routes.py        <- Roteamento das páginas HTML (como Router do React)
├── websocket.py     <- Comunicação real-time com JS no front
├── controllers/     <- Lógica de negócios (consultas, simulações)
├── templates/       <- HTML + Jinja2 (ex: vindo do DeepSite)
├── static/          <- CSS, JS, imagens (também exportado do DeepSite)
├── dashboards/      <- Dash apps (ex: dashboard de desempenho)
```

## 📊 Contribuindo  

1. Faça um **fork** do repositório.  
2. Crie uma nova branch para sua funcionalidade:  
   ```bash
   git checkout -b nome-da-funcionalidade
   ```  
3. Commit suas alterações e abra um **Pull Request**.  
