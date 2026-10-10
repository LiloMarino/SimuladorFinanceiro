---
sidebar_position: 8
---

# Estatísticas da Simulação

A tela de **Estatísticas** mostra o desempenho de cada jogador por dimensão, como a tela de fim de partida de um jogo de estratégia: uma aba por assunto, cada uma com gráficos ao longo do tempo e uma tabela por jogador.

Enquanto a **Carteira** mostra os seus ativos, as **Estatísticas** respondem quem está indo melhor, quanto risco cada um correu para chegar lá e de onde veio o resultado.

O mesmo relatório aparece em três lugares:

- **Durante a partida**, pelo menu **Estatísticas**. Ele se atualiza a cada virada de mês.
- **Na comparação entre simulações**, pelo botão **Comparar Simulações** do lobby. Cada série aparece como `Jogador#Simulação`.
- **No fechamento da partida**.

Todas as métricas são calculadas no simulador a partir do patrimônio de cada dia útil. Cada uma tem um ícone **i** com a definição, um exemplo e como ler o número.

:::info A cota: retorno sem contar aportes
Várias métricas usam a **cota**, como a de um fundo de investimento: um valor que começa em 1 e só se move com o que os investimentos renderam. O aporte mensal entra como capital, não como ganho. Ex.: se o patrimônio foi de R$ 10.000 para R$ 22.000, mas R$ 12.000 vieram de aportes, a cota continua em 1,00, e o retorno é zero.
:::

---

## Geral

- **Resumo da partida:** a sua posição, o seu retorno, a média da sala e o melhor e o pior retorno.
- **Ranking de jogadores:** posição, patrimônio, retorno em R$ e em % sobre o capital aportado (saldo inicial + aportes) e quantos dias foram simulados.

---

## Rentabilidade

- **Retorno acumulado:** a variação da cota desde o primeiro dia, uma linha por jogador. As linhas tracejadas são as referências do mesmo período:
  - **CDI:** o que um título de 100% do CDI teria rendido.
  - **Ibovespa:** a variação do índice da bolsa.

  Acima das duas, a carteira bateu tanto a renda fixa quanto a bolsa.
- **Patrimônio:** caixa + investimentos, dia a dia, com os aportes.
- **Tabela:**
  - **Capital aportado.**
  - **Retorno anual:** a cota composta para um ano. Ex.: +2% em 63 pregões (~3 meses) equivale a ~8,2% ao ano.
  - **Meses acima do CDI:** ex.: "9 de 12" quer dizer que bateu o CDI em 75% dos meses.
  - **Meses no positivo.**

  As linhas do CDI e do Ibovespa trazem o retorno anual de cada referência para comparar.

---

## Risco

- **Distância do pico:** quanto a cota de cada jogador está abaixo do maior valor que já alcançou, dia a dia. Zero é estar no topo.
- **Volatilidade em janela móvel:** a volatilidade anual calculada só com os últimos 63 pregões (~3 meses). Mostra os períodos agitados e os calmos.
- **Risco × retorno:** um ponto por jogador. Para a direita é mais oscilação; para cima, mais retorno. Quanto mais para cima e para a esquerda, melhor.
- **Tabela:**

| Métrica | O que mede | Como ler |
| --- | --- | --- |
| **Queda máxima** (drawdown) | A maior queda a partir de um pico. Ex.: subiu a R$ 15.000 e caiu a R$ 12.000 → 20% | Quanto menor, melhor; acima de ~30% é uma queda que a maioria não aguenta sem vender |
| **Volatilidade anual** | O tamanho típico da oscilação diária, em ritmo de um ano (desvio-padrão × √252) | ~1% é renda fixa; ~25% é uma carteira só de ações |
| **Índice de Sharpe** | (retorno anual − CDI anual) ÷ volatilidade. Ex.: 18% de retorno, CDI de 10%, volatilidade de 16% → 0,50 | Abaixo de 0 perdeu para o CDI; perto de 1 é bom; acima de 2 é raro |
| **Índice de Sortino** | Como o Sharpe, mas só a oscilação dos dias abaixo do CDI conta como risco | Mesma leitura do Sharpe; fica acima dele quando as oscilações são mais para cima |
| **Maior tempo abaixo do pico** | A maior sequência de pregões até voltar ao topo. Ex.: caiu em março e recuperou em setembro → ~126 pregões | Quanto menor, melhor; 252 pregões é um ano inteiro abaixo do topo |
| **Pior mês** | O pior retorno mensal da cota. Ex.: −5% → cada R$ 1.000 virou R$ 950 | Quanto mais perto de zero, melhor |
| **Amostra** | Quantos retornos diários entraram no cálculo | Abaixo de ~63 pregões, as métricas mudam muito de um dia para o outro |

---

## Composição

- **Composição do patrimônio:** caixa, renda variável e renda fixa empilhados, dia a dia, de um jogador por vez (escolhido nos botões acima do gráfico).
- **Exposição por setor:** uma barra por jogador, dividida pela fração da renda variável em cada setor no último dia. Mostra quem apostou em quê. Ao lado, o **número efetivo de setores**: 1 ÷ a soma dos quadrados das frações. Tudo num setor dá 1; dividido igual em 4 setores dá 4; 70/10/10/10 dá ~1,9, quase um setor só. Abaixo de 2 é uma carteira concentrada.
- **Lucro por setor:** de onde veio o resultado da renda variável de cada jogador, setor a setor. É o que entrou nas vendas, menos o que saiu nas compras, mais o valor do que ainda está na carteira, antes do IR. Verde é lucro, vermelho é prejuízo.

O setor e o segmento de cada ação vêm da [Central de dados](./importacao-ativos#setor-e-segmento-das-ações).

---

## Operações

- **Volume negociado por mês:** quanto cada jogador comprou e vendeu em ações a cada mês.
- **Tabela:**
  - **Compras** e **vendas:** cada execução conta uma vez; uma ordem preenchida em partes conta várias.
  - **Volume negociado.**
  - **Giro:** volume ÷ patrimônio médio. Ex.: patrimônio médio de R$ 100 mil e R$ 300 mil negociados → 3,00.
  - **IR pago.**
  - **Custo de impacto:** com o impacto de preço ligado, é o preço executado menos o preço histórico em cada negócio. Comprar acima e vender abaixo do histórico é custo; o contrário é ganho, e aparece negativo.

---

## Próximos Passos

- [Carteira](./carteira) - Veja seus ativos individuais
- [Investimentos Suportados](./investimentos/renda-variavel) - Aprenda mais sobre tipos de investimento
