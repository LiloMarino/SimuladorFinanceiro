---
sidebar_position: 1.5
---

# Análise técnica

O gráfico do detalhe da ação mostra, além do preço, os **indicadores técnicos**: linhas e painéis que resumem a tendência e a força do preço a partir do próprio histórico. Embaixo do gráfico, o **Resumo técnico** lê todos eles no fechamento do dia e diz para que lado a maioria aponta.

Os indicadores olham só para o passado. Eles descrevem o que o preço fez, com regras fixas: são um retrato do dia, não uma previsão.

## Ligar e ajustar os indicadores

O botão **Indicadores**, acima do gráfico, abre o seletor. O número ao lado dele conta quantos estão ligados.

- **Sobre o preço**: médias móveis e Bandas de Bollinger, desenhadas por cima do preço.
- **Painéis embaixo do gráfico**: volume, IFR, MACD, estocástico, ATR e OBV, cada um no seu painel.

Cada linha tem uma chave para ligar e desligar e, à direita, os parâmetros atuais (por exemplo, **14** no IFR). Clicar neles abre os campos para editar. O gráfico muda na hora, sem botão de salvar.

As escolhas valem para todas as ações da partida e ficam salvas para o seu jogador. **Restaurar padrão** volta os parâmetros aos valores da tabela abaixo.

Na primeira visita nada vem ligado. O aviso **Novo: indicadores técnicos** oferece **Ligar a média de 20**, o jeito mais simples de começar.

A legenda acima do gráfico traz o valor de cada linha no último pregão. Com o mouse sobre o gráfico, um quadro ao lado da mira mostra a data, o fechamento e as linhas sobre o preço, e a legenda e os rótulos dos painéis passam a mostrar o dia apontado.

Também dá para desligar sem abrir o seletor: com o mouse sobre um item da legenda aparece um **X** que tira aquela linha. No rótulo de cada painel, a engrenagem abre os parâmetros dele no seletor e o **X** desliga o painel.

## Os indicadores

| Indicador | Parâmetros padrão | Onde aparece |
|---|---|---|
| Média móvel simples (MMS) | 20 pregões | Sobre o preço |
| Média móvel exponencial (MME) | 50 pregões | Sobre o preço |
| Bandas de Bollinger | 20 pregões, 2 desvios | Sobre o preço |
| Volume | — | Painel |
| IFR | 14 pregões, faixas 70 e 30 | Painel |
| MACD | 12, 26 e 9 pregões | Painel |
| Estocástico | 14 e 3 pregões | Painel |
| ATR | 14 pregões | Painel |
| OBV | — | Painel |

Dá para ter até 4 médias ao mesmo tempo, cada uma simples ou exponencial e com o próprio período.

### Médias móveis

A **média móvel simples** é a média dos fechamentos dos últimos N pregões. Ela suaviza o sobe e desce do dia a dia e mostra a tendência. Ex.: fechamentos de R$ 10, R$ 11 e R$ 12 dão uma média de 3 pregões de R$ 11.

A **média móvel exponencial** dá mais peso aos pregões recentes, então reage mais rápido a uma virada.

**Como ler:** preço acima da média indica tendência de alta, e o resumo lê **Compra**. Preço abaixo da média indica tendência de baixa, e o resumo lê **Venda**. Ex.: PETR4 fecha a R$ 7,51 com a MMS 20 em R$ 7,64. O preço está abaixo da média, então a leitura é Venda.

### Bandas de Bollinger

Uma faixa em volta da média de 20 pregões, com 2 desvios-padrão para cima e para baixo. O desvio-padrão mede o quanto o preço costuma se afastar da média. Quanto mais o preço oscila, mais larga fica a faixa. Na maior parte do tempo o preço fica dentro dela.

**Como ler:** fechar acima da banda de cima é sinal de que o preço subiu além do normal, e o resumo lê **Venda**. Abaixo da banda de baixo, **Compra**. Dentro da faixa, **Neutro**. Ex.: a faixa vai de R$ 7,25 a R$ 8,02, e o preço de R$ 7,51 está dentro dela, então a leitura é Neutro.

### Volume

Quantas ações trocaram de mão no dia. A barra é verde quando a ação fechou acima da abertura e vermelha quando fechou abaixo. Volume alto mostra que muita gente negociou naquele preço. O volume não entra no resumo.

### IFR (Índice de Força Relativa)

Compara o tamanho das altas com o das quedas nos últimos 14 pregões e devolve um número de 0 a 100. Ex.: se as altas somaram o triplo das quedas, o IFR fica em 75.

**Como ler:**

- **Acima de 70**: a ação subiu rápido demais (sobrecomprada), e o resumo lê **Venda**.
- **Abaixo de 30**: a ação caiu rápido demais (sobrevendida), e o resumo lê **Compra**.
- **Entre 30 e 70**: o resumo lê **Neutro**.

As duas faixas são editáveis. Um período menor reage mais rápido e cruza as faixas mais vezes.

### MACD

A diferença entre uma média exponencial curta (12 pregões) e uma longa (26 pregões). A **linha de sinal** é a média de 9 pregões dessa diferença. As barras mostram a distância entre as duas linhas.

**Como ler:** linha acima do sinal mostra que a tendência de alta está ganhando força, e o resumo lê **Compra**. Linha abaixo do sinal, **Venda**. Ex.: MACD em −0,05 com o sinal em −0,03. A linha está abaixo do sinal, então a leitura é Venda.

### Estocástico

Mostra onde o fechamento ficou entre a mínima e a máxima dos últimos 14 pregões, de 0 a 100. A linha %K é esse valor, e a linha %D é a média de 3 pregões dela. Ex.: mínima de R$ 10, máxima de R$ 20 e fechamento de R$ 18 dão 80, perto do topo da faixa.

**Como ler:** acima de 80 o resumo lê **Venda**. Abaixo de 20, **Compra**. No meio, **Neutro**.

### ATR

Quanto o preço anda por dia, em reais, na média dos últimos 14 pregões. Ex.: ATR de R$ 0,14 significa que a ação costuma variar uns 14 centavos entre a mínima e a máxima do dia.

O ATR mede o tamanho do movimento, não a direção. Por isso aparece no resumo como **Sem lado** e fica fora da conta.

### OBV

Um saldo de volume que soma o volume dos dias de alta e subtrai o dos dias de queda. O valor em si importa pouco: o que conta é a direção do saldo.

**Como ler:** saldo maior que 5 pregões atrás mostra mais volume nas altas, e o resumo lê **Compra**. Saldo menor, **Venda**.

## Resumo técnico

O card embaixo do gráfico lê, no fechamento do dia, os **7 indicadores que apontam um lado**: MMS, MME, Bollinger, IFR, MACD, estocástico e OBV. Ele lê todos, ligados no gráfico ou não, com os parâmetros do seletor, inclusive os editados. Se houver mais de uma média do mesmo tipo, o resumo lê a primeira da lista.

As leituras ficam em duas colunas: **Médias e faixa** e **Osciladores**. Cada linha traz o valor do dia, a leitura (**Compra**, **Neutro**, **Venda** ou **Sem lado**) e o porquê. Com o mouse sobre a linha aparece a regra completa.

### Como sai o veredito

A nota é o número de compras menos o de vendas, dividido pelo número de indicadores lidos:

> nota = (compras − vendas) ÷ indicadores lidos

Ela vai de −1 (todos apontam venda) a +1 (todos apontam compra), e o ponteiro mostra onde ela caiu:

| Nota | Veredito |
|---|---|
| 0,5 ou mais | Compra forte |
| de 0,2 a 0,5 | Compra |
| de −0,2 a 0,2 | Neutro |
| de −0,5 a −0,2 | Venda |
| abaixo de −0,5 | Venda forte |

Ex.: 1 indicador aponta compra, 3 apontam venda e 3 ficam neutros. A nota é (1 − 3) ÷ 7 = −0,29, entre −0,5 e −0,2, então o veredito é **Venda**.

### Pouco histórico

Cada indicador precisa de alguns pregões antes de ter valor: a MMS 20 precisa de 20, e o IFR 14 precisa de 15. Enquanto falta histórico, a linha do resumo mostra quantos pregões faltam, e a legenda do gráfico mostra quando o indicador aparece.

O veredito só sai quando a maioria dos 7 indicadores (pelo menos 4) já tem valor. Antes disso, o card mostra **Ainda sem leitura** e a partir de quantos pregões o resumo aparece.

## Padrões de vela

No gráfico de **Velas**, o interruptor **Padrões de vela** (ligado por padrão) marca as formas de vela que costumam anteceder uma alta ou uma baixa. Cada marcação traz o nome curto sobre a vela: seta verde embaixo quando o padrão sugere alta, vermelha em cima quando sugere baixa e um ponto cinza no doji, que só mostra indecisão. Padrão de várias velas ganha também uma faixa atrás dele. O interruptor lembra a sua escolha.

| Padrão | Velas | Sugere |
|---|---|---|
| Martelo | 1, depois de uma queda | Alta |
| Martelo invertido | 1, depois de uma queda | Alta |
| Engolfo de alta | 2 | Alta |
| Estrela da manhã | 3 | Alta |
| Três soldados brancos | 3 | Alta |
| Enforcado | 1, depois de uma alta | Baixa |
| Estrela cadente | 1, depois de uma alta | Baixa |
| Engolfo de baixa | 2 | Baixa |
| Estrela da tarde | 3 | Baixa |
| Três corvos negros | 3 | Baixa |
| Doji | 1 | Nenhum (indecisão) |

Com o mouse sobre um padrão aparece o card **E se ele acertou?**, com o desenho animado da forma, o que ela conta sobre o pregão e o histórico do padrão naquela ação. Os 5 pregões seguintes ficam contornados no gráfico.

**Como ler "acertou":** o padrão acerta quando o fechamento do 5º pregão depois dele vai para o lado que ele sugeriu. Ex.: um martelo fecha a R$ 10,00; cinco pregões depois o fechamento é R$ 10,40. O preço subiu, então o martelo acertou. Se fechasse a R$ 9,80, errou.

**Amostra:** o percentual só aparece com 10 ocorrências ou mais. "61% de 31" quer dizer que, em 31 vezes que o padrão apareceu naquela ação, 19 acertaram. Com menos de 10 o card só conta quantas vezes ele apareceu, porque "100% de 3" não diz nada. Mesmo um percentual alto não é promessa: o padrão errou nas outras vezes.

No gráfico de **Linha**, os marcadores não aparecem; um aviso conta quantos padrões há no período e o botão **Ver em velas** troca o gráfico. Se não há padrão no período, o aviso diz isso e oferece o período maior mais próximo que tem.

### Lista dos padrões

Embaixo do gráfico, a seção **Padrões neste período** lista cada padrão com a data, o lado, o nome, a variação do preço em 5 pregões e ✓ ou ✕. Fechada, ela mostra só a contagem e quantos acertaram ("X de Y"); o doji não aposta em lado e fica fora dessa conta. Clicar numa linha leva o gráfico até o padrão e abre o card. A seção lembra se você a deixou aberta.

### Desafio da vela

Quando um padrão com lado aparece no último pregão, uma faixa acima do gráfico pergunta **sobe ou desce?** até o fechamento do 5º pregão seguinte. Você responde com **▲ Sobe** ou **▼ Desce**, e a resposta vale até o pregão seguinte: sem resposta, o desafio passa e não conta.

- **Acertou ou errou:** o resultado sai no fechamento do 5º pregão. Preço igual ao do padrão anula a pergunta.
- **Placar:** a faixa mostra "acertos de respostas" na partida. O doji não gera desafio.
- **Fim da partida:** o cartão **Desafio da vela** lista quem mais acertou. Ele não entra na nota nem no ranking.
- **Conquistas:** **Primeira leitura** (1 acerto) e **Leitor de velas** (10 acertos).

## Legendas nos indicadores

Com as dicas ligadas, os indicadores ganham legendas curtas sobre o gráfico:

- **IFR:** "Sobrecomprado" na linha de 70 e "Sobrevendido" na de 30, com o que cada um costuma significar.
- **MACD e médias móveis:** um círculo em cada cruzamento (a linha do MACD cruzando o sinal; uma média cruzando outra) e uma frase só no último, dizendo o que o cruzamento costuma indicar. Nas médias, só com 2 ou mais ligadas.

As dicas de análise técnica (padrões, desafio, avisos, legendas e o cartão do fim da partida) somem no **Modo Especialista** ou com **Esconder dicas de análise técnica** ligado em [Assistências](../lobby#assistências-modo-especialista).

## Os mesmos números das estratégias

As estratégias automáticas usam as mesmas contas do gráfico. A estratégia de IFR, por exemplo, decide pelo mesmo IFR que aparece no painel.
