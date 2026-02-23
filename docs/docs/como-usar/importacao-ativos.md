---
sidebar_position: 7
---

# Importação de Ativos

O simulador permite importar dados históricos de ativos para usar na simulação. Esta funcionalidade é essencial para ter acesso a ações, FIIs e ETFs com dados reais de mercado.

## Como Funciona

O sistema de importação carrega **dados históricos OHLCV** (Open, High, Low, Close, Volume) de ativos e os armazena no banco de dados para uso nas simulações.

**OHLCV significa:**
- **Open (Abertura)** - Preço na abertura do dia
- **High (Máxima)** - Preço mais alto do dia
- **Low (Mínima)** - Preço mais baixo do dia
- **Close (Fechamento)** - Preço no fechamento do dia
- **Volume** - Quantidade de ações negociadas no dia

Estes dados são usados para simular o movimento realista do mercado durante a simulação.

![Exemplo de tela de importação de ativos](/img/importar.png)

---

## Métodos de Importação

### 1. Yahoo Finance (yfinance)

O simulador pode buscar dados diretamente do **Yahoo Finance** usando a biblioteca `yfinance`.

**Como importar:**

1. Acesse **Configurações** → **Importar Ativos**
2. No card **Buscar via yFinance**, informe o **Código do Ativo** (ex: `PETR4`, `VALE3`, `BTC-USD`)
3. (Opcional) Marque **Sobrescrever dados existentes**
4. Clique em **Buscar e Importar**
5. Confirme a ação na janela de confirmação

**Exemplos de tickers brasileiros:**
- Ações: `VALE3.SA`, `PETR4.SA`, `BBAS3.SA`, `ITUB4.SA`
- FIIs: `XPML11.SA`, `HGLG11.SA`, `MXRF11.SA`
- ETFs: `BOVA11.SA` (Ibovespa), `SMAL11.SA` (Small Caps)

:::warning Limitações do Yahoo Finance
A importação via Yahoo Finance depende da **API externa** deles, que pode ter:
- **Limitações de requisições** - Muitas requisições simultâneas podem ser bloqueadas
- **Indisponibilidade** - O serviço pode estar fora do ar temporariamente
- **Dados incompletos** - Alguns ativos podem não ter dados para todos os períodos
- **Atrasos** - Dados podem estar desatualizados (geralmente 1 dia de atraso)

Se você encontrar problemas, tente novamente mais tarde ou use a importação via CSV.
:::

---

### 2. Arquivo CSV Customizado

Você pode importar dados de qualquer fonte usando um **arquivo CSV** no formato aceito.

**Como importar:**

1. Prepare seu arquivo CSV no formato correto (veja abaixo)
2. Acesse **Configurações** → **Importar Ativos**
3. No card **Importar via CSV**, informe o **Nome do Ativo**
4. Selecione o **arquivo CSV**
5. (Opcional) Marque **Sobrescrever dados existentes**
6. Clique em **Importar CSV**
7. Confirme a ação na janela de confirmação

#### Formato do CSV

O arquivo CSV deve ter as seguintes colunas **obrigatórias**:

```csv
Date,Open,High,Low,Close,Volume
2020-01-02,50.00,52.00,49.50,51.50,1000000
2020-01-03,51.50,53.00,51.00,52.80,1200000
2020-01-06,52.80,54.00,52.50,53.50,1100000
```

**Especificações:**
- **Date** - Data no formato `YYYY-MM-DD` (ex: `2020-01-02`)
- **Open** - Preço de abertura (número decimal, use `.` para separador decimal)
- **High** - Preço máximo
- **Low** - Preço mínimo
- **Close** - Preço de fechamento
- **Volume** - Volume negociado (número inteiro)

**Regras:**
- ✅ Primeira linha deve ser o cabeçalho (nome das colunas)
- ✅ Datas devem estar em ordem cronológica crescente
- ✅ Não pode haver datas duplicadas
- ✅ Não pode haver linhas vazias
- ✅ Valores numéricos devem usar `.` (ponto) como separador decimal

**Exemplo de arquivo CSV válido:**

[📄 Baixe o arquivo de exemplo](/csv/exemplo-importacao-ohlcv.csv)


## Dicas Rápidas

- Use **Sobrescrever dados existentes** quando quiser atualizar um ticker que ja existe.
- A importação pede confirmação antes de enviar os dados.
