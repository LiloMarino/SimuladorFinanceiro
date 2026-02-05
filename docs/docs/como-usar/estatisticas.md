---
sidebar_position: 8
---

# Estatísticas da Simulação

A tela de **Estatísticas da Simulação** oferece métricas avançadas de desempenho e é especialmente útil em **sessões multiplayer**, onde você pode comparar seu desempenho com outros jogadores.

## O que é a tela de Estatísticas?

Enquanto a **Carteira** foca nos seus ativos individuais, a tela de **Estatísticas** foca em **métricas de desempenho agregadas** e **comparações**.

Esta tela é particularmente valiosa em modo multiplayer, onde você compete com outros jogadores e quer saber:
- Quem está ganhando?
- Como estou me saindo comparado aos outros?
- Quais estratégias estão funcionando melhor?

<!-- Espaço reservado para screenshot da tela de estatísticas -->

---

## O que você pode observar

### Ranking de Jogadores

**Lista ordenada por patrimônio:**
- Mostra todos os jogadores na sessão
- Ordenados do maior para o menor patrimônio
- Você pode ver sua posição no ranking

**Para cada jogador, mostra:**
- **Nome/Nickname**
- **Patrimônio Total** - Valor total (dinheiro + investimentos)
- **Rentabilidade (%)** - Quanto cresceu desde o início (ex: +15,5%)
- **Posição no Ranking** - 1º, 2º, 3º lugar, etc.

:::tip Competição Saudável
Use o ranking para se motivar, mas lembre-se: o objetivo é aprender sobre investimentos, não apenas ganhar!
:::

---

### Métricas Individuais de Desempenho

#### Retorno Total (%)

Percentual de valorização do seu patrimônio desde o início da simulação.

**Fórmula:**
```
Retorno (%) = ((Patrimônio Atual - Capital Inicial) / Capital Inicial) × 100
```

**Exemplo:**
- Capital Inicial: R$ 10.000
- Patrimônio Atual: R$ 12.500
- Retorno: +25%

---

#### Retorno Anualizado (%)

Retorno médio anual, considerando o tempo decorrido na simulação.

**Por que é importante:**
- Permite comparar simulações de diferentes durações
- É a métrica padrão do mercado financeiro

**Exemplo:**
- Simulação de 6 meses com retorno de 10%
- Retorno Anualizado: ~20% ao ano

---

#### Sharpe Ratio

Mede a relação entre retorno e risco (volatilidade).

**O que significa:**
- **Alto Sharpe (> 1,5)** - Bom retorno com baixo risco
- **Sharpe médio (0,5 - 1,5)** - Retorno razoável para o risco
- **Baixo Sharpe (< 0,5)** - Muito risco para o retorno obtido

**Por que é importante:**
Dois jogadores podem ter o mesmo retorno, mas um deles pode ter assumido muito mais risco. O Sharpe Ratio ajuda a identificar estratégias mais eficientes.

---

#### Máximo Drawdown (%)

Maior queda do patrimônio em relação ao pico anterior.

**O que significa:**
- Mostra a maior perda que você teve em algum momento
- Importante para entender o risco da estratégia

**Exemplo:**
- Seu patrimônio chegou a R$ 15.000 (pico)
- Depois caiu para R$ 12.000 (vale)
- Drawdown: -20%

**Por que é importante:**
Drawdowns grandes podem ser psicologicamente difíceis de suportar. Saber o drawdown ajuda a avaliar se a estratégia é sustentável.

---

#### Número de Operações

Total de compras e vendas realizadas.

**O que indica:**
- **Muitas operações** - Estratégia ativa (day trade, swing trade)
- **Poucas operações** - Estratégia passiva (buy and hold)

---

#### Taxa de Acerto (Win Rate)

Percentual de operações que resultaram em lucro.

**Fórmula:**
```
Win Rate = (Operações Lucrativas / Total de Operações) × 100
```

**O que significa:**
- **> 60%** - Alta taxa de acerto
- **40-60%** - Taxa média
- **< 40%** - Baixa taxa de acerto

:::info Importante
Uma taxa de acerto alta não garante lucro! É possível ter 70% de acerto mas prejuízo geral se as operações perdedoras forem muito grandes.
:::

---

### Comparações com Benchmark

**O que é benchmark:**
Um benchmark é um índice de referência usado para comparar o desempenho.

**Benchmarks comuns:**
- **Ibovespa** - Principal índice da bolsa brasileira
- **CDI** - Taxa referência para renda fixa
- **Inflação (IPCA)** - Para medir retorno real

**O que você pode ver:**
- Seu retorno vs. retorno do benchmark
- Se você está "batendo o mercado" (retorno maior que o benchmark)

**Exemplo:**
```
Seu Retorno: +20%
Ibovespa: +15%
Resultado: Você bateu o mercado em 5 pontos percentuais! 🎉
```

---

### Gráficos e Visualizações

#### Evolução Patrimonial Comparativa

**Gráfico de linhas** mostrando a evolução do patrimônio de todos os jogadores ao longo do tempo:

- Cada jogador é uma linha de cor diferente
- Fácil visualizar quem está na frente e quem está atrás
- Permite ver momentos de ultrapassagem

#### Composição de Portfólio

**Gráfico de pizza ou barra** mostrando:
- % em Renda Variável vs. Renda Fixa
- % em cada setor (tecnologia, energia, bancos, etc.)
- % em cada ativo individual

---

## Quando Usar a Tela de Estatísticas

### Durante a Simulação

- Verificar sua posição no ranking
- Ajustar estratégia se estiver ficando para trás
- Aprender com jogadores que estão indo bem

### Após a Simulação

- Analisar o desempenho final
- Entender o que funcionou e o que não funcionou
- Comparar diferentes estratégias testadas

### Em Multiplayer

- Competição amigável
- Ver estratégias de outros jogadores (em tempo real)
- Discutir táticas e aprender em grupo

---

## Dicas para Melhorar suas Estatísticas

### Para Aumentar Retorno
- Diversifique entre renda variável e fixa
- Busque ativos com bom potencial
- Não tenha medo de assumir risco calculado

### Para Reduzir Risco (Drawdown)
- Diversifique seu portfólio
- Use stop loss em posições perdedoras
- Tenha sempre uma parte em renda fixa

### Para Melhorar Sharpe Ratio
- Busque ativos com boa relação risco/retorno
- Evite concentração excessiva
- Considere rebalancear o portfólio periodicamente

---

## Diferença: Carteira vs. Estatísticas

| Aspecto | Carteira | Estatísticas |
|---------|----------|--------------|
| **Foco** | Ativos individuais | Métricas agregadas |
| **Uso** | Gestão diária | Análise de desempenho |
| **Multiplayer** | Mostra só suas posições | Mostra todos os jogadores |
| **Métricas** | Básicas (P&L, valor) | Avançadas (Sharpe, Drawdown) |
| **Quando usar** | Durante operações | Para análise estratégica |

---

## Próximos Passos

- [Carteira](./carteira) - Veja seus ativos individuais
- [Investimentos Suportados](./investimentos/renda-variavel) - Aprenda mais sobre tipos de investimento
