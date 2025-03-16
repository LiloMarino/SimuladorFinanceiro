# Projeto Simulador Financeiro

## 📌 Visão Geral
Este projeto é um **simulador financeiro interativo**, inspirado em jogos RTS como **Hearts of Iron e Victoria 3**, focado no **mercado financeiro brasileiro**. O objetivo é testar estratégias de negociação e investimento, oferecendo um ambiente dinâmico onde o usuário pode interagir comprando e vendendo ativos. A simulação inclui tanto **renda fixa (CDB, LCI, LCA, Tesouro Direto)** quanto **renda variável (Ações, FIIs, ETFs)**, com funcionalidades que permitem um acompanhamento detalhado do portfólio.

## 🎮 Modos de Jogo
### 1️⃣ **Modo Automático** 📈  
- O tempo avança automaticamente como em um RTS.  
- As compras e vendas são executadas com base em uma estratégia programada.  
- O usuário pode escolher ou testar diferentes estratégias.  

### 2️⃣ **Modo Manual** 🏦  
- O jogador pode **emitir ordens de compra e venda manualmente**.  
- O mercado segue em tempo real, e o usuário decide quando intervir.  
- O tempo avança continuamente, mas pode ser pausado ou acelerado (**1x, 2x, 4x, 10x**).  

## 🔥 Funcionalidades Principais
✅ **Simulação de negociações** em tempo real (Ações, FIIs, ETFs).  
✅ **Investimentos em renda fixa** (CDB, LCI, LCA, Tesouro Direto).  
✅ **Salário mensal**: Simulação de renda periódica.  
✅ **Análise de desempenho**: Retorno, drawdown, índice de Sharpe, etc.  
✅ **Eventos econômicos**: Crises, mudanças de juros e inflação.  
✅ **Gráficos interativos** com **Plotly**.  
✅ **Interface Web** amigável usando **Streamlit**.  
✅ **Suporte a múltiplas fontes de dados** (Yahoo Finance, APIs da B3, etc.).  

## 🛠️ Tecnologias Utilizadas
- **[Backtrader](https://www.backtrader.com/)** → Motor de backtesting e simulação.  
- **[Streamlit](https://streamlit.io/)** → Interface gráfica interativa.  
- **[Plotly](https://plotly.com/python/)** → Gráficos dinâmicos.  
- **[yfinance](https://pypi.org/project/yfinance/)** → Dados do mercado financeiro.  
- **Banco de Dados (MySQL ou SQLite)** → Armazenamento de históricos e portfólio.  

## 🚀 Roadmap do Desenvolvimento
### 📌 Fase 1: Estrutura Base
- [ ] Configurar ambiente e dependências (Backtrader, Streamlit, Plotly, yfinance).  
- [ ] Criar estrutura inicial do projeto e banco de dados.  
- [ ] Implementar coleta de dados (Yahoo Finance + outras fontes).  
- [ ] Criar sistema de portfólio e saldo inicial do usuário.  

### 📌 Fase 2: Implementação do Mercado
- [ ] Criar lógica de simulação de mercado com Backtrader.  
- [ ] Implementar regras de compra e venda.  
- [ ] Configurar investimentos em renda fixa.  
- [ ] Adicionar eventos econômicos dinâmicos.  

### 📌 Fase 3: Interface Gráfica (Streamlit)
- [ ] Criar painel de **gráficos interativos** com Plotly.  
- [ ] Criar **botões de compra/venda** para o modo manual.  
- [ ] Implementar **botão de pause/play** e controle de velocidade.  

### 📌 Fase 4: Testes e Refinamento
- [ ] Testar e ajustar estratégias de negociação.  
- [ ] Ajustar **métricas de desempenho** (Sharpe, Drawdown, etc.).  
- [ ] Testar estabilidade e desempenho do simulador.  
- [ ] Documentar código e criar tutoriais.  

## Configuração
1. **Dependências Python**:
    - Instale o Python 3.9 ou superior.
    - Instale as bibliotecas necessárias:
      ```bash
      pip install backtrader pandas matplotlib yfinance
      ```

2. **Fontes de Dados**:
    - Renda variável: Utilize o Yahoo Finance ou Alpha Vantage para dados históricos (ex.: PETR4.SA para Petrobras).
    - Renda fixa: Simule os retornos baseados em índices (ex.: CDI, IPCA).

3. **Estrutura do Projeto**:
    ```plaintext
    /simulador-financeiro
    ├── data/                # Pasta para armazenar conjuntos de dados baixados
    ├── strategies/          # Estratégias personalizadas de negociação
    ├── assets/              # Configuração de diferentes ativos (ações, FIIs, renda fixa)
    ├── utils/               # Funções auxiliares
    ├── main.py              # Ponto de entrada para executar simulações
    ├── requirements.txt     # Lista de dependências
    └── README.md            # Documentação
    ```

## Como Executar
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-repositorio/simulador-financeiro.git
   cd simulador-financeiro
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute a simulação:
   ```bash
   python main.py
   ```

## Contribuindo
1. Faça um fork do repositório.
2. Crie uma nova branch para sua funcionalidade:
   ```bash
   git checkout -b nome-da-funcionalidade
   ```
3. Commit suas alterações e abra um Pull Request.

---
Sinta-se à vontade para contribuir ou sugerir funcionalidades para este projeto!
