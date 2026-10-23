---
sidebar_position: 6
---

# Carteira

A **Carteira** é a tela inicial da partida: ela reúne tudo o que você tem, quanto isso vale e quanto ainda falta pagar de imposto.

![A carteira com o patrimônio, a alocação e os indicadores do dia](/demo/screens/portfolio.png)

## Patrimônio e alocação

No topo, o **Patrimônio líquido** soma o caixa e tudo o que está investido e desconta o que você deve em [Crédito](./credito.md). Sem dívida, é o total do que você tem.

A faixa **Alocação** mostra quanto está investido e em que parte do patrimônio isso pesa. Ela divide o patrimônio em três: **Renda variável**, **Renda fixa** e **Caixa**, cada uma com o valor e o percentual.

Nas partidas de corrida à meta e de viver de renda, o patrimônio mostra também quanto da meta você já cumpriu (por exemplo, "42% da meta de R$ 1.000.000"). A tela [Meta](./meta.md) detalha essa corrida.

## Indicadores do dia

Um card com as taxas de referência do dia simulado. Cada indicador tem um ícone **i** que mostra a explicação resumida.

- **CDI**: taxa diária dos empréstimos entre bancos, base de muitos CDBs. O card mostra a taxa **anual equivalente** à do dia: quanto o CDI renderia em um ano se a taxa do dia se repetisse em todos os 252 dias úteis do ano, com os ganhos rendendo também no dia seguinte (juros compostos). Ex.: a taxa diária de 0,0551% equivale a 14,9% ao ano.
- **SELIC**: taxa básica de juros da economia, definida pelo Banco Central. Aparece do mesmo jeito que o CDI.
- **IPCA 12m**: inflação acumulada nos últimos 12 meses até o mês simulado. Ex.: 4,5% significa que o que custava R$ 100 doze meses antes passou a custar R$ 104,50.

Ex.: em 02/01/2020, o card mostra **CDI 4,40%**, **SELIC 4,40%** e **IPCA 12m 4,19%**.

## Evolução do patrimônio

Um gráfico de área com o patrimônio ao longo do tempo simulado. Cada faixa é uma classe (**Caixa**, **Renda fixa** e **Renda variável**), e o topo da pilha é o patrimônio total.

Por cima das faixas passa uma linha tracejada com o que você aportou. Enquanto o topo do gráfico está acima dela, você está no ganho; abaixo, no prejuízo. Nas partidas de meta, uma linha pontilhada marca a meta de cada dia.

Antes do primeiro pregão simulado o gráfico fica vazio: cada dia que passa vira um ponto.

## Distribuição dos investimentos

Uma pizza que separa o que está em renda variável e em renda fixa. O caixa fica de fora: o gráfico mostra só o dinheiro investido.

## Renda variável

A tabela lista cada ação, FII ou ETF da carteira:

| Coluna | O que mostra |
|---|---|
| **Ativo** | O ticker do papel |
| **Qtd.** | A posição total |
| **Preço médio** | O preço médio de compra |
| **Preço atual** | A cotação do dia simulado |
| **Valor** | O valor de mercado da posição |
| **% carteira** | A participação no patrimônio |
| **Resultado** | O ganho ou a perda em R$ e em %, em verde ou vermelho |

Clicar numa linha abre a página do ativo, onde você negocia. Sem nenhuma posição, a tabela mostra "Nenhuma ação na carteira".

## Renda fixa

A tabela lista cada título aplicado:

| Coluna | O que mostra |
|---|---|
| **Título** | O nome do título |
| **Aplicado** | O valor que você aplicou |
| **Valor atual** | O valor corrigido até o dia simulado |
| **Taxa** | A rentabilidade contratada |
| **% carteira** | A participação no patrimônio |
| **Resultado** | O ganho ou a perda em R$ e em % |

Clicar numa linha abre a página do título. Sem nenhuma aplicação, a tabela mostra "Nenhum título na carteira".

## Renda variável por setor

Barras com a fração da renda variável em cada setor, e uma tabela com o valor e a fração de cada setor e de cada segmento dentro dele. Um selo no topo resume quantos setores a carteira tem e o grau de diversificação.

- Ex.: R$ 6.000 em bancos e R$ 4.000 em mineração → Financeiro 60%, Materiais Básicos 40%.
- Ações sem classificação aparecem como **Sem setor**; a classificação se edita na [Central de dados](./importacao-ativos#setor-e-segmento-das-ações).

## Imposto de renda

O card **Imposto de renda** acompanha o imposto sobre o lucro das suas vendas em renda variável:

- **Já pago**: o imposto que já saiu do seu caixa.
- **A pagar**: o imposto que ainda vai sair. Quando há valor, o card diz em que dia ele sai do caixa e de qual mês são as vendas.
- **Vendas de ações no mês**: uma régua com o quanto você já vendeu em ações. O lucro com ações é isento enquanto as vendas do mês somarem até R$ 20.000.

As regras são as do Brasil: 15% do lucro em ações (isento até a régua acima), 20% em FIIs e em day trade, e 15% em ETFs e BDRs, sem isenção. O botão **Como funciona** abre esse resumo.

## Próximos passos

- [Estatísticas da simulação](./estatisticas): métricas de desempenho e ranking
- [Importação de ativos](./importacao-ativos): adicionar novos ativos à simulação
