---
sidebar_position: 4
---

# Lobby

O lobby é onde você configura os parâmetros da simulação antes de iniciá-la. Esta página explica o que cada campo faz e como eles influenciam a simulação.

## Campos de Configuração

### Nome da Sessão

**O que é:** Um nome identificador para sua simulação.

**Influência:** Não afeta a simulação em si, apenas facilita identificar a sessão na lista de salas disponíveis (especialmente em multiplayer).

**Exemplo:** "Competição de Ações 2024", "Teste de Renda Fixa"

---

### Capital Inicial

**O que é:** A quantia de dinheiro que cada jogador começa na simulação.

**Influência:** 
- Determina quanto dinheiro você tem disponível para investir no início
- Todos os jogadores começam com o mesmo valor em multiplayer
- Valores mais altos permitem diversificar mais rapidamente

**Valores típicos:** 
- R$ 10.000 - Simulação realista para iniciantes
- R$ 100.000 - Portfólio mais robusto
- R$ 1.000.000 - Cenários avançados

---

### Data de Início

**O que é:** A data inicial da simulação no histórico de mercado.

**Influência:**
- Define a partir de qual ponto histórico os dados de mercado serão utilizados
- Permite simular diferentes períodos econômicos (crises, bull markets, etc.)
- Dados históricos disponíveis geralmente de 2000 até 2026

**Exemplo:** 
- "2008-01-01" - Simular a crise de 2008
- "2020-03-01" - Simular o crash da COVID-19
- "2010-01-01" - Período de crescimento econômico

:::tip
Escolher períodos históricos específicos permite testar suas estratégias em diferentes cenários de mercado.
:::

---

### Data de Término

**O que é:** A data final da simulação no histórico de mercado.

**Influência:**
- Define até quando a simulação vai rodar
- Quando a data de término é atingida, a simulação para automaticamente
- A diferença entre data de início e término define a "duração" da simulação

**Exemplo:**
- Se início é "2020-01-01" e término é "2021-01-01", a simulação cobre 1 ano de dados históricos

:::info
A velocidade da simulação (1x, 2x, 4x, 10x) afeta quão rápido você progride entre estas datas, não as datas em si.
:::

---

### Contribuição Mensal

**O que é:** Um valor que é automaticamente adicionado ao seu saldo todo mês simulado.

**Influência:**
- Simula aportes mensais regulares (estratégia comum de investimento)
- Permite testar estratégias de acumulação a longo prazo
- Em multiplayer, todos recebem a mesma contribuição mensal

**Valores típicos:**
- R$ 0 - Sem aportes mensais
- R$ 500 - R$ 2.000 - Aportes realistas para pessoa física
- R$ 5.000+ - Cenários de alta capacidade de investimento

**Exemplo:**
Se você configurar R$ 1.000 de contribuição mensal:
- A cada mês simulado, R$ 1.000 serão automaticamente adicionados ao seu saldo disponível
- Com velocidade 10x, isto acontece 10 vezes mais rápido em tempo real

---

### Ativos Disponíveis

**O que é:** A lista de ativos (ações, FIIs, ETFs, renda fixa) que estarão disponíveis para negociação na simulação.

**Influência:**
- Define quais investimentos você poderá fazer
- Mais ativos = mais opções de diversificação
- Menos ativos = simulação mais focada e simples

**Como configurar:**
- Você pode importar ativos do Yahoo Finance (dados históricos reais)
- Ou importar dados de CSV próprios
- Também pode escolher ativos de renda fixa disponíveis (CDB, LCI, LCA, Tesouro Direto)

:::info
Os dados de ativos são carregados antes de iniciar a simulação. Veja [Importação de Ativos](../importacao-ativos) para mais detalhes.
:::

---

## Dicas de Configuração

### Para Iniciantes
```
Capital Inicial: R$ 10.000
Data Início: 2020-01-01
Data Término: 2021-01-01
Contribuição Mensal: R$ 1.000
Velocidade: 1x ou 2x
```

### Para Competições Multiplayer
```
Capital Inicial: R$ 100.000 (igual para todos)
Data Início: 2015-01-01
Data Término: 2020-01-01 (5 anos de dados)
Contribuição Mensal: R$ 0 (sem aportes, testar só estratégia)
Velocidade: 2x ou 4x
```

### Para Testar Crises
```
Capital Inicial: R$ 50.000
Data Início: 2008-01-01 (início da crise)
Data Término: 2010-01-01
Contribuição Mensal: R$ 2.000
Velocidade: 4x
```

---

## Próximos Passos

Após configurar o lobby:

1. Clique em "Iniciar Simulação"
2. Aguarde o carregamento dos dados de mercado
3. Comece a investir! Veja [Investimentos Suportados](../investimentos/renda-variavel) para aprender mais
