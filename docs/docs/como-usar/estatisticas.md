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
- **Ranking de jogadores:** ordenado pela **nota geral**. Mostra também patrimônio, retorno em R$ e em % sobre o capital aportado (saldo inicial + aportes) e quantos dias foram simulados. Quem ainda não tem nota vem depois, e o retorno desempata.
- **Nota:** a decomposição da nota de cada jogador, eixo por eixo e métrica por métrica (ex.: "Queda máxima 13,65% → 72,7 pts"). Mostra o que puxou a nota para baixo.

### Como a nota é calculada

A nota resume num número só quatro **eixos**: Retorno, Risco, Consistência e Eficiência. Cada eixo junta métricas que olham o desempenho por ângulos diferentes, e os eixos pesam igual entre si. Assim, nenhum lado conta em dobro: ter quatro métricas de risco não faz o risco valer mais que o retorno.

**1. Cada métrica vira pontos** por uma reta com dois níveis fixos: o valor que vale 0 ponto ($$x_0$$) e o que vale 100 pontos ($$x_{100}$$). O chão é 0 e **não há teto**:

$$
\text{pontos}(x) = \max\left(0,\ 100 \cdot \frac{x - x_0}{x_{100} - x_0}\right)
$$

**2. Cada eixo é a média dos pontos das suas métricas.** Uma métrica que ainda não pode ser medida (ex.: o Sharpe de uma carteira que não oscila) sai da média:

$$
\text{eixo} = \frac{1}{n} \sum_{i=1}^{n} \text{pontos}_i
$$

**3. A nota é a soma dos quatro eixos:**

$$
\text{nota} = R + K + C + E
$$

em que $$R$$ é o eixo Retorno, $$K$$ o Risco, $$C$$ a Consistência e $$E$$ a Eficiência.

| Eixo | Métrica | Vale 0 | Vale 100 |
| --- | --- | --- | --- |
| Retorno | Retorno anual acima do CDI | −10 p.p. | +10 p.p. |
| Retorno | Retorno anual acima do Ibovespa | −15 p.p. | +15 p.p. |
| Risco | Queda máxima | 50% | 0% |
| Risco | Volatilidade anual | 40% | 0% |
| Risco | Maior tempo abaixo do pico | 252 pregões | 0 |
| Risco | Pior mês | −20% | 0% |
| Consistência | Meses acima do CDI | 0% dos meses | 100% |
| Consistência | Meses no positivo | 0% dos meses | 100% |
| Eficiência | Índice de Sharpe | −1 | 2 |
| Eficiência | Índice de Sortino | −1 | 3 |

**Como ler:** ~100 pontos num eixo é um desempenho bom, então ~400 é ir bem em tudo. As faixas são fixas, iguais em toda partida, então a nota de partidas diferentes se compara (na tela de comparação, por exemplo).

**Exemplo:** rendeu 4,83 p.p. ao ano acima do CDI (74,2 pts) e 2,28 p.p. abaixo do Ibovespa (42,4 pts) → Retorno 58,3. Queda máxima de 13,65% (72,7), volatilidade de 19,10% (52,2), 59 pregões abaixo do pico (76,6) e pior mês de −2,90% (85,5) → Risco 71,8. Bateu o CDI em 33% dos meses (33,3) e ficou no positivo em 50% (50,0) → Consistência 41,7. Sharpe de 0,31 (43,8) e Sortino de 0,48 (36,9) → Eficiência 40,4. **Nota: 58,3 + 71,8 + 41,7 + 40,4 = 212.**

:::note Por que sem teto, e o que isso muda
Como num placar de jogo, a nota não tem limite em cima. Mas risco e consistência têm um máximo natural: risco zero vale 100, e não dá para bater o CDI em mais de 100% dos meses. Já retorno e eficiência crescem sem limite. Por isso, quem ganha muito acima do CDI pode compensar um risco maior. Um jogador que deixa tudo parado em caixa fica com ~100, quase todos vindos do eixo Risco.
:::

:::info A nota aparece a partir de 63 pregões
Com pouco tempo de partida, anualizar engana: 10 dias com +2% viram ~64% ao ano. Por isso a nota só aparece depois de 63 pregões (~3 meses). Antes disso, o ranking ordena pelo retorno.
:::

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
