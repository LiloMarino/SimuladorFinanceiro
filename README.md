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
✅ **Gráficos interativos** em **Plotly** para acompanhar a evolução do portfólio.  
✅ **Interface Web** intuitiva via **Streamlit**.  
✅ **Suporte a múltiplas fontes de dados** (Yahoo Finance, MySQL, SQLite).  
✅ **Modo Multiplayer** com servidor cliente-servidor.  
✅ **Empacotamento como executável (.exe)** para facilitar a distribuição.  

## 🛠️ Tecnologias Utilizadas  

- **[Backtrader](https://www.backtrader.com/)** → Motor de backtesting e simulação.  
- **[Streamlit](https://streamlit.io/)** → Interface gráfica interativa.  
- **[Plotly](https://plotly.com/python/)** → Gráficos dinâmicos.  
- **[yfinance](https://pypi.org/project/yfinance/)** → Dados do mercado financeiro.  
- **Banco de Dados** → **MySQL e SQLite** para armazenamento de históricos e portfólio.  
- **WebSockets** → Comunicação em tempo real para o modo multiplayer.  
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

4. **Estrutura do Projeto**:  
   ```plaintext
   /simulador-financeiro
   ├── data/                # Dados históricos baixados
   ├── strategies/          # Estratégias de negociação automatizadas
   ├── assets/              # Configuração de ativos (ações, FIIs, renda fixa)
   ├── utils/               # Funções auxiliares
   ├── main.py              # Ponto de entrada do simulador
   ├── server.py            # Servidor do modo multiplayer
   ├── requirements.txt     # Lista de dependências
   └── README.md            # Documentação
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

3. Inicie a interface gráfica (modo local):  
   ```bash
   streamlit run main.py
   ```  

4. Para ativar o **modo multiplayer**, inicie o servidor antes de conectar os clientes:  
   ```bash
   python server.py
   ```  

## 📊 Contribuindo  

1. Faça um **fork** do repositório.  
2. Crie uma nova branch para sua funcionalidade:  
   ```bash
   git checkout -b nome-da-funcionalidade
   ```  
3. Commit suas alterações e abra um **Pull Request**.  

---

Sinta-se à vontade para contribuir ou sugerir novas funcionalidades! 🚀