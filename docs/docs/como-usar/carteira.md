---
sidebar_position: 6
---

# Carteira

A **Carteira** (ou Portfólio) é onde você visualiza e gerencia todos os seus investimentos em um só lugar.

## O que é a Carteira?

A carteira é uma tela centralizada que mostra uma visão completa da sua posição financeira na simulação. Ela agrega todos os seus ativos e permite acompanhar o desempenho do seu portfólio em tempo real.

![Exemplo de tela de carteira](/img/carteira.png)

## O que você pode observar na Carteira

### Visão Geral

**Patrimônio Total**
- Valor total da carteira (dinheiro + investimentos)
- Exibe a rentabilidade total em %

**Total Investido**
- Soma do valor investido nas posições
- Mostra o percentual do patrimônio alocado

**Renda Variável**
- Valor total em ações/FIIs/ETFs
- Percentual da carteira em renda variável

**Renda Fixa**
- Valor total em títulos de renda fixa
- Percentual da carteira em renda fixa

---

### Renda Variável

**Tabela de Posições:**
Para cada ativo de renda variável, a carteira mostra:

- **Ativo** - Ticker do papel
- **Preço Médio** - Preço médio de compra
- **Preço Atual** - Cotação atual
- **Quantidade** - Posição total
- **Valor Total** - Valor de mercado da posição
- **% Carteira** - Participação no portfólio
- **Retorno (R$)** - Ganho/perda absoluto
- **Retorno (%)** - Ganho/perda percentual
- **Ações** - Atalho para **Detalhes** do ativo

**Gráfico de Distribuição:**
- Visualização em pizza com a composição total da carteira
- Inclui renda variável e renda fixa

**Renda Variável por Setor:**
- Barras com a fração da renda variável em cada setor, e uma tabela com o valor e a fração de cada setor e de cada segmento dentro dele
- Ex.: R$ 6.000 em bancos e R$ 4.000 em mineração → Financeiro 60%, Materiais Básicos 40%
- Ações sem classificação aparecem como **Sem setor**; a classificação se edita na [Central de dados](./importacao-ativos#setor-e-segmento-das-ações)

---

### Renda Fixa

**Tabela de Investimentos:**
Para cada ativo de renda fixa, a carteira mostra:

- **Ativo** - Nome do título
- **Valor Investido** - Valor aplicado
- **Valor Atual** - Valor atualizado
- **Taxa** - Rentabilidade do título
- **% Carteira** - Participação no portfólio
- **Retorno (R$)** - Ganho/perda absoluto
- **Retorno (%)** - Ganho/perda percentual
- **Ações** - Atalho para **Detalhes** do ativo

---

### Indicadores Econômicos

Um card com as taxas de referência do dia simulado. Cada indicador tem um ícone **i** que mostra a explicação resumida.

- **CDI** - taxa diária dos empréstimos entre bancos, base de muitos CDBs. O card mostra a taxa **anual equivalente** à do dia: quanto o CDI renderia em um ano se a taxa do dia se repetisse em todos os 252 dias úteis do ano, com os ganhos rendendo também no dia seguinte (juros compostos). Ex.: a taxa diária de 0,0551% equivale a 14,9% ao ano.
- **SELIC** - taxa básica de juros da economia, definida pelo Banco Central. Aparece do mesmo jeito que o CDI.
- **IPCA (12m)** - inflação acumulada nos últimos 12 meses até o mês simulado. Ex.: 4,5% significa que o que custava R$ 100 doze meses antes passou a custar R$ 104,50.

Ex.: em 02/01/2020, o card mostra **CDI 4,40%**, **SELIC 4,40%** e **IPCA (12m) 4,19%**.

---

### Evolução do Patrimônio

**Gráfico de Linha:**
- Mostra o histórico do patrimônio ao longo do tempo simulado
- Útil para acompanhar tendência e volatilidade

---

## Próximos Passos

- [Estatísticas da Simulação](./estatisticas) - Métricas de desempenho e ranking
- [Importação de Ativos](./importacao-ativos) - Adicionar novos ativos à simulação
