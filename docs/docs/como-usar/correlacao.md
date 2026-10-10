---
sidebar_position: 9
---

# Correlação entre Ativos

A tela de **Correlação** mostra o quanto os ativos andam juntos, antes de você montar uma carteira ou uma estratégia. Diversificar só funciona entre ativos que não caem ao mesmo tempo. Sem essa medida, duas posições "diferentes" podem ser a mesma aposta.

Ela abre em dois lugares:

- **Durante a partida**, pelo menu **Correlação**. A janela termina sempre na data da simulação, para a ferramenta não revelar o futuro.
- **No lobby**, pelo botão **Correlação entre ativos**. Aqui a janela pode terminar em qualquer dia: o campo **Termina em** começa no último pregão importado.

---

## Como usar

1. Marque os ativos na lista à esquerda (até 20).
2. Escolha a **janela**: 6 meses, 1 ano, 3 anos ou 5 anos até a data final.
3. Leia o mapa de calor. Cada célula é um par de ativos, e o **Ibovespa** entra como última linha e coluna, como referência do mercado.

Passe o mouse numa célula para ver o valor, a faixa de leitura e quantos pregões em comum entraram no cálculo.

---

## O que é a correlação

A correlação compara os **retornos diários** de dois ativos: a variação de cada pregão sobre o pregão anterior. Ela responde se, nos dias em que um sobe mais que o normal, o outro também sobe. O resultado vai de −1 a 1:

| Valor | Leitura |
| --- | --- |
| 0,7 a 1 | Andam muito juntos |
| 0,3 a 0,7 | Andam juntos em parte |
| −0,3 a 0,3 | Quase independentes |
| −1 a −0,3 | Tendem a ir em direções opostas |

**Exemplo:** em 2023, ITUB4 e o Ibovespa tiveram correlação de 0,74. Nos dias de queda da bolsa, o Itaú costumava cair junto. No mesmo ano, ITUB4 e PETR4 ficaram em 0,27: um banco e uma petroleira respondem, na maior parte dos dias, a notícias diferentes.

**Para diversificar, quanto mais baixa, melhor.** Duas ações com 0,9 de correlação somam praticamente o mesmo risco. Duas com 0,2 se compensam em parte: quando uma cai, a outra muitas vezes não cai.

A cor ajuda a ler a grade: **vermelho** para correlação positiva (andam juntos), **azul** para negativa (vão em direções opostas). Quanto mais forte a cor, mais longe de zero.

:::info Correlação não é causa
Uma correlação alta diz que os dois ativos se movem juntos, não que um move o outro. Normalmente os dois respondem à mesma coisa: juros, câmbio, o humor da bolsa.
:::

---

## Pregões em comum

Cada célula usa só os pregões em que **os dois** ativos negociaram, então a amostra muda de célula para célula. Uma ação listada há pouco tempo tem menos dias em comum com as outras.

- Com menos de **20 pregões em comum** (~1 mês), a célula mostra **—**. Com tão poucos dias, o número seria ruído.
- Com menos de **63 pregões** (~3 meses), a correlação muda muito de uma janela para outra. Leia com cautela.
- Um dia sem preço válido no banco conta como dia sem pregão: o retorno seguinte cobre os dois dias.

---

## Por que o CDI não entra como referência

O "retorno diário" do CDI é a taxa do dia, que só muda quando o Copom mexe na Selic. Comparado com uma ação, que varia todo dia, ele quase não se move. Por isso a correlação com o CDI fica perto de 0 e não ensina nada. Numa janela em que a Selic não mudou, ela nem existe: não há como medir se dois ativos andam juntos quando um deles ficou parado.
