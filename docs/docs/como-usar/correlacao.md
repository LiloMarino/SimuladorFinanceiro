---
sidebar_position: 9
---

# Correlação entre Ativos

A tela de **Correlação** mostra o quanto os ativos andam juntos, antes de você montar uma carteira ou uma estratégia. Diversificar só funciona entre ativos que não caem ao mesmo tempo. Sem essa medida, duas posições "diferentes" podem ser a mesma aposta.

![A matriz de correlação entre um ativo de cada setor](/demo/screens/correlation.png)

Ela abre em dois lugares:

- **Durante a partida**, pelo menu **Correlação**. A janela termina sempre na data da simulação, para a ferramenta não revelar o futuro.
- **No lobby**, pelo card **Correlação entre ativos**. Aqui a janela pode terminar em qualquer dia: o campo **Data final da janela** começa no último pregão importado e não passa dele.

---

## Como usar

1. Marque os ativos na lista à esquerda, agrupada por setor (até 20). Os atalhos **Minha carteira** (na partida) e **Um de cada setor** marcam vários de uma vez.
2. Escolha a **janela**: 6 meses, 1 ano, 3 anos ou 5 anos até a data final. Com menos de dois ativos marcados, a tela pede que você escolha pelo menos dois.
3. Leia a matriz. Cada célula é um par de ativos; como o par A × B é o mesmo que B × A, a matriz mostra só a metade de baixo. O **Ibovespa** fica numa linha à parte, como referência do mercado.

Clique numa célula para fixar o par no painel ao lado: o valor, a faixa de leitura e quantos pregões em comum entraram no cálculo. O painel também traz os **destaques**: o par que mais anda junto, o melhor par para diversificar (a menor correlação) e, na partida, a correlação média entre as ações da sua carteira.

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

A cor ajuda a ler a grade: **vermelho** para correlação positiva (andam juntos), **azul** para negativa (vão em direções opostas). Quanto mais forte a cor, mais longe de zero. A legenda da grade resume a escala: −1 são opostos, 0 são independentes e 1 andam juntos.

:::info Correlação não é causa
Uma correlação alta diz que os dois ativos se movem juntos, não que um move o outro. Normalmente os dois respondem à mesma coisa: juros, câmbio, o humor da bolsa.
:::

---

## Pregões em comum

Cada célula usa só os pregões em que **os dois** ativos negociaram, então a amostra muda de célula para célula. Uma ação listada há pouco tempo tem menos dias em comum com as outras.

- Com menos de **63 pregões em comum** (~3 meses), a célula mostra **—**. Com menos dias que isso, a correlação muda muito de uma janela para outra e o número seria ruído. Clicando na célula, o painel diz quantos pregões havia e o que fazer: aumentar a janela ou esperar a partida avançar.
- Se um dos dois ficou parado a janela inteira, a célula também mostra **—**: sem variação, não dá pra medir se andam juntos.
- Um dia sem preço válido no banco conta como dia sem pregão: o retorno seguinte cobre os dois dias.

---

## Por que o CDI não entra como referência

O "retorno diário" do CDI é a taxa do dia, que só muda quando o Copom mexe na Selic. Comparado com uma ação, que varia todo dia, ele quase não se move. Por isso a correlação com o CDI fica perto de 0 e não ensina nada. Numa janela em que a Selic não mudou, ela nem existe: não há como medir se dois ativos andam juntos quando um deles ficou parado.
