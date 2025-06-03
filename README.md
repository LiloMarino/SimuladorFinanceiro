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
- **Banco de Dados** → **MySQL e SQLite** para armazenamento de históricos e portfólio.  
- **WebSockets** → Comunicação em tempo real para atualização de gráficos e multiplayer.  
- **PyInstaller** → Empacotamento da aplicação como executável (.exe).  

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
│
├── main.py                # Ponto de entrada da aplicação Flask
├── requirements.txt       # Lista de dependências
├── README.md              # Documentação
└── server.py              # Servidor do modo multiplayer
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

## 📜 Licença

Este projeto está licenciado sob os termos da [Licença Pública Geral GNU, versão 3 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.html).

Você pode usar, modificar e redistribuir este software livremente, contanto que preserve a mesma licença em versões modificadas.

© 2025 Murilo Marino

