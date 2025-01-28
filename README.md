# Projeto Simulador Financeiro

## Visão Geral
Este projeto simula o mercado financeiro brasileiro para testar estratégias de negociação e investimento. Ele combina tanto renda fixa (ex.: CDB, LCI, LCA, Tesouro Direto) quanto renda variável (ex.: Ações, FIIs, ETFs). A simulação inclui funcionalidades como salário mensal, gerenciamento de portfólio e métricas de desempenho, todas adaptadas ao mercado brasileiro.

## Funcionalidades
- **Simulação de negociações em tempo real**: Comprar e vender ações, FIIs e ETFs.
- **Simulação de investimentos em renda fixa**: Acompanhar retornos de CDB, LCI, LCA e Tesouro Direto.
- **Salário mensal**: Adicionar renda periódica para simular um pagamento regular.
- **Análise de desempenho**: Mensurar a eficácia das estratégias com métricas como retorno, drawdown e índice de Sharpe.
- **Foco no Brasil**: Inclui ativos e dados relevantes ao mercado financeiro brasileiro.

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

## Issues

### Desenvolvimento do MVP
1. **Motor de Simulação Principal**  
   - **Descrição**: Configurar o motor do Backtrader para simular o gerenciamento de portfólio.
   - **Tarefas**:
     - Inicializar o "Cerebro" do Backtrader com um saldo de caixa padrão.
     - Adicionar lógica para rastrear um portfólio de investimentos em renda fixa e variável.
     - Permitir fluxo de caixa periódico (salário mensal).
   - **Etiquetas**: `simulação`, `backtrader`

2. **Integração de Dados de Renda Variável**  
   - **Descrição**: Integrar ações, FIIs e ETFs brasileiros utilizando o Yahoo Finance.
   - **Tarefas**:
     - Obter dados históricos para PETR4.SA, VALE3.SA, etc.
     - Garantir que os dados sejam ajustados para dividendos e splits.
     - Testar o carregamento no Backtrader.
   - **Etiquetas**: `dados`, `integração`

3. **Simulação de Renda Fixa**  
   - **Descrição**: Simular retornos de renda fixa com base no CDI ou IPCA.
   - **Tarefas**:
     - Criar uma classe genérica para ativos de renda fixa.
     - Calcular juros compostos diários ou mensais.
     - Integrar ao portfólio do Backtrader.
   - **Etiquetas**: `renda fixa`, `simulação`

4. **Métricas de Desempenho**  
   - **Descrição**: Adicionar métricas para avaliar o sucesso das estratégias.
   - **Tarefas**:
     - Incluir retorno, índice de Sharpe e drawdown.
     - Exibir as métricas como parte dos resultados da simulação.
   - **Etiquetas**: `análise`, `desempenho`

### Melhorias
5. **Interface Amigável**  
   - **Descrição**: Criar um painel para interagir com a simulação.
   - **Tarefas**:
     - Utilizar Streamlit ou Dash para o frontend.
     - Exibir portfólio, transações e métricas de desempenho.
   - **Etiquetas**: `frontend`, `painel`

6. **Testes de Cenários**  
   - **Descrição**: Adicionar suporte para simulação de cenários hipotéticos.
   - **Tarefas**:
     - Implementar cenários de choque no mercado (ex.: quedas bruscas).
     - Permitir simulações parametrizadas (ex.: diferentes níveis de salário).
   - **Etiquetas**: `simulação`, `cenários`

7. **Análises Avançadas**  
   - **Descrição**: Adicionar insights mais profundos sobre o desempenho das estratégias.
   - **Tarefas**:
     - Comparar estratégias lado a lado.
     - Visualizar diversificação de portfólio e exposição ao risco.
   - **Etiquetas**: `análise`, `melhorias`

### Documentação
8. **Escrever Documentação**  
   - **Descrição**: Criar guias para uso e extensão do simulador.
   - **Tarefas**:
     - Escrever um guia para execução de simulações.
     - Documentar o processo de configuração e personalizações.
   - **Etiquetas**: `documentação`

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

## Roadmap
- [x] Configuração básica do Backtrader
- [ ] Integração com renda fixa
- [ ] Simulação de salário mensal
- [ ] Interface com painel
- [ ] Testes de cenários

## Contribuindo
1. Faça um fork do repositório.
2. Crie uma nova branch para sua funcionalidade:
   ```bash
   git checkout -b nome-da-funcionalidade
   ```
3. Commit suas alterações e abra um Pull Request.

---
Sinta-se à vontade para contribuir ou sugerir funcionalidades para este projeto!
