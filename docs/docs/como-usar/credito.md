---
sidebar_position: 8.5
---

# Crédito

A tela **Crédito** deixa você pegar dinheiro emprestado para investir e acompanhar o que deve. O empréstimo entra no caixa na hora e vira parcelas fixas, debitadas do caixa na data de cada uma.

A dívida pesa no ranking: o **patrimônio líquido** é tudo o que você tem investido e em caixa **menos** o que ainda deve.

## A nota de risco

Sua **nota de risco** vai de **AAA** (a melhor) até **D** e vem de uma pontuação de 0 a 100, que soma três partes:

- **Alavancagem (até 40 pontos):** quanto da sua riqueza é dívida. Sem dívida vale 40; cada 10% de dívida sobre o patrimônio líquido tira 4 pontos. Ex.: R$ 100 mil de dívida com R$ 400 mil de patrimônio é 25% e dá 30 pontos.
- **Volatilidade (até 30 pontos):** o quanto o patrimônio balança, medido pelo tamanho típico das oscilações diárias levado para um ano. De 0% a 45% ao ano a nota perde pontos aos poucos; a partir de 45% vale zero. Com menos de 21 pregões de histórico, conta como 0%.
- **Pagamentos em dia (até 30 pontos):** cada parcela atrasada nos últimos 12 meses tira 10 pontos.

A alavancagem e a volatilidade são recalculadas no fim de cada mês. Parcela atrasada derruba a nota na hora.

| Nota | Pontos | Juro | Dívida até |
| --- | --- | --- | --- |
| AAA | 90 a 100 | SELIC + 3 | 100% do patrimônio |
| AA | 80 a 89 | SELIC + 4 | 80% |
| A | 70 a 79 | SELIC + 5 | 60% |
| BBB | 60 a 69 | SELIC + 6,5 | 45% |
| BB | 50 a 59 | SELIC + 8 | 30% |
| B | 40 a 49 | SELIC + 10 | 20% |
| CCC | 30 a 39 | SELIC + 13 | 10% |
| D | 0 a 29 | sem crédito novo | 0% |

O "+ 3", "+ 5" e os demais são pontos percentuais por ano somados à SELIC. Ex.: nota A com a SELIC em 4,25% paga 4,25% + 5 = **9,25% ao ano**. Se a renda fixa mais cara do dia rende mais que isso, o juro sobe para essa taxa mais 0,5 ponto, para que pegar emprestado e aplicar em renda fixa nunca seja ganho garantido.

## Contratar um empréstimo

1. Digite o **valor** (até o limite que a sua nota permite) e escolha o **prazo**, de 6 a 60 parcelas.
2. A tela mostra a **parcela**, o **juro total** e o rendimento da renda fixa mais cara no mesmo prazo, para você comparar.
3. Clique em **Revisar e assinar**. O dinheiro cai no caixa e o juro fica travado até o fim do contrato.

As parcelas seguem a **Tabela Price**: o valor é sempre o mesmo, mas no começo a maior parte é juro e, a cada mês, o juro cai e a parte que abate a dívida cresce. Ex.: R$ 50.000 em 24 parcelas a 9,25% ao ano dá parcela de **R$ 2.281,48** e **R$ 4.755,40** de juro no total.

## Pagar antes

Em **Seus empréstimos**, **Amortizar** paga uma parte e **Quitar** paga tudo. Como o juro só corre sobre o que falta, pagar antes abate os juros que ainda não correram. Ao amortizar, você escolhe se a economia reduz o **prazo** (mesma parcela, menos meses) ou a **parcela** (mesmos meses, parcela menor).

## Parcela atrasada

Se não houver caixa na data, a parcela fica **em atraso**: cobra-se uma multa única de 2% e uma mora de 1% ao mês (simples, por dia corrido) sobre a parcela. A linha do empréstimo fica destacada com o botão **Pagar** e a nota cai na hora. Um aviso chega 7 dias antes de uma parcela sem caixa.

Quando o patrimônio líquido fica negativo (a dívida passa do que você tem), você aparece como **Negativado** nas estatísticas e no ranking.

## Onde a dívida aparece

- **Carteira:** o patrimônio vira **Patrimônio líquido**, com o detalhe de ativos, dívida e quanto dos ativos é financiado.
- **Estatísticas:** a aba Risco tem a tabela **Dívida na sala** e a aba Rentabilidade mostra o juro pago e o custo da dívida (o juro médio dos seus empréstimos, dando mais peso aos de maior saldo) ao lado do retorno do período.
- **Menu:** o item **Crédito** ganha um ponto vermelho quando há parcela em atraso.
