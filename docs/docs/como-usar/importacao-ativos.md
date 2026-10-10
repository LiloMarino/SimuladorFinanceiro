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

## Central de dados

A **Central de dados** é a tela onde você importa ações e acompanha quais séries estão guardadas no banco. Ela substitui a antiga tela "Importar Ativos" e é aberta pelo botão **Central de dados** no lobby.

Ela só pode ser aberta **fora de uma partida**: durante uma partida, o sistema leva você de volta para a tela principal.

A tela tem duas partes: os formulários de importação de ações (explicados nas seções abaixo) e a tabela **Séries da base**.

### Séries da base

A tabela lista todas as séries guardadas no banco: primeiro os indicadores econômicos (CDI, SELIC, IPCA e Ibovespa) e depois cada ação importada. Em cada linha:

- **Série**: nome do indicador ou do ticker.
- **Início**: primeira data com dado.
- **Fim do dado real**: última data com dado publicado pela fonte.
- **Fim do dado gerado**: sempre "—" por enquanto. Fica reservada para dados que o simulador venha a gerar no futuro.
- **Linha do tempo**: barra com o período coberto pelo dado real. Todas as barras usam a mesma régua de tempo, então dá para comparar visualmente quais séries cobrem mais anos. Passe o mouse sobre a barra para ver as datas.
- **Ação**: botão **Atualizar** da linha.

### Indicadores econômicos

- **CDI**: taxa de juros dos empréstimos entre bancos, publicada por dia. Serve de base para muitos CDBs. Ex.: um CDI de 0,0551% em um dia quer dizer que R$ 1.000 viram R$ 1.000,55 na noite.
- **SELIC**: taxa básica de juros da economia, definida pelo Banco Central e também publicada por dia.
- **IPCA**: inflação oficial, medida por mês. Ex.: um IPCA de 0,5% no mês significa que os preços subiram 0,5% naquele mês.
- **Ibovespa**: índice que acompanha o desempenho das ações mais negociadas da B3, a bolsa brasileira. Ex.: de 100.000 para 101.000 pontos é uma alta de 1%.

**Fontes:** CDI, SELIC e IPCA vêm do Banco Central, pelo sistema SGS (Sistema Gerenciador de Séries Temporais), nas séries 12 (CDI diário), 11 (SELIC diária) e 433 (IPCA mensal). O Ibovespa vem do Yahoo Finance (ticker `^BVSP`).

### Atualização

- **Atualizar** (em um indicador) busca esse indicador na fonte na hora.
- **Atualizar todos** atualiza todos os indicadores e as ações cujo último preço tem mais de 2 dias.
- Ações com dados desatualizados aparecem destacadas em **vermelho**.

Ao iniciar, o app também busca os indicadores sozinho, no máximo uma vez a cada 6 horas. Sem internet, os dados já guardados continuam valendo e o app segue funcionando normalmente.

---

## Métodos de Importação

### 1. Yahoo Finance (yfinance)

O simulador pode buscar dados diretamente do **Yahoo Finance** usando a biblioteca `yfinance`.

**Como importar:**

1. Acesse a **Central de dados** (botão no lobby)
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
2. Acesse a **Central de dados** (botão no lobby)
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
- Antes de escolher o período no lobby, confira na **Central de dados** até quando cada série tem dado real.
