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

<!-- Espaço reservado para screenshot da tela de importação -->

---

## Métodos de Importação

### 1. Yahoo Finance (yfinance)

O simulador pode buscar dados diretamente do **Yahoo Finance** usando a biblioteca `yfinance`.

**Como importar:**

1. Acesse **Configurações** → **Importar Ativos** → **Yahoo Finance**
2. Digite o **ticker** do ativo (ex: `VALE3.SA`, `PETR4.SA`)
   - **Importante:** Ativos brasileiros precisam do sufixo `.SA` (São Paulo)
3. Escolha o **período** (data inicial e final)
4. Clique em **Importar**
5. Aguarde o download dos dados
6. O ativo estará disponível para uso na próxima simulação

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
2. Acesse **Configurações** → **Importar Ativos** → **CSV**
3. Faça upload do arquivo
4. O sistema validará o formato
5. Se válido, os dados serão importados
6. O ativo estará disponível para uso na próxima simulação

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

<!-- Link para arquivo CSV de exemplo -->

---

## Onde Obter Dados CSV

Se você quiser usar dados de fontes alternativas ao Yahoo Finance:

### Fontes de Dados de Mercado

1. **B3 (Bolsa Brasileira)**
   - Site oficial da B3 disponibiliza alguns dados históricos
   - [http://www.b3.com.br/](http://www.b3.com.br/)

2. **Status Invest**
   - Plataforma brasileira com dados de ações e FIIs
   - [https://statusinvest.com.br/](https://statusinvest.com.br/)

3. **Quantum Axis**
   - API paga com dados do mercado brasileiro

4. **Alpha Vantage**
   - API gratuita (com limitações) para dados internacionais

:::tip Dica
Após baixar dados de qualquer fonte, você pode precisar convertê-los para o formato CSV aceito pelo simulador. Use Excel, Google Sheets ou Python para fazer a conversão.
:::

---

## Gestão de Ativos Importados

### Visualizar Ativos Disponíveis

1. Acesse **Configurações** → **Ativos Importados**
2. Veja a lista de todos os ativos já importados
3. Verifique:
   - Ticker
   - Nome
   - Período de dados disponíveis
   - Data da última importação

### Atualizar Dados

Para atualizar dados de um ativo:

1. Re-importe o ativo com novos dados
2. O sistema substituirá os dados antigos pelos novos
3. **Atenção:** Simulações em andamento usarão os dados antigos até serem reiniciadas

### Deletar Ativos

Para remover um ativo:

1. Acesse **Configurações** → **Ativos Importados**
2. Selecione o ativo
3. Clique em **Deletar**
4. Confirme

:::warning
Deletar um ativo não afeta simulações já criadas, mas ele não estará disponível para novas simulações.
:::

---

## Perguntas Frequentes

**P: Quantos ativos posso importar?**  
R: Não há limite técnico, mas importar muitos ativos pode deixar o banco de dados grande e a interface pesada.

**P: Posso importar ativos internacionais?**  
R: Sim, via Yahoo Finance ou CSV. Use tickers do Yahoo Finance (ex: `AAPL` para Apple, `TSLA` para Tesla).

**P: O que acontece se eu importar dados incompletos?**  
R: A simulação pode funcionar com gaps (dias sem dados), mas a precisão será afetada. Recomendamos dados completos.

**P: Posso editar dados depois de importar?**  
R: Atualmente não. Você precisaria deletar e re-importar com dados corretos.

---

## Próximos Passos

Após importar ativos:

1. [Crie uma simulação no Lobby](./lobby)
2. Selecione os ativos importados para uso
3. Comece a investir!
