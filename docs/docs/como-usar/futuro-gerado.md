---
sidebar_position: 7.5
---

# Como o futuro é gerado

Os dados reais acabam no último pregão importado. Para a partida ir além do presente, o simulador gera um **futuro plausível**: preços das ações, Ibovespa, SELIC, CDI e IPCA para os dias seguintes. Esse futuro é gravado na base como dado comum, marcado como "gerado", e a partida o lê como lê o histórico.

Esta página explica como ele é montado, de onde vem cada regra e o quanto ele se parece com o mercado de verdade.

---

## A ideia: montar o futuro com peças reais

Muitos jogos geram fases montando **peças desenhadas à mão**: o Spelunky sorteia salas prontas e as encaixa uma na outra. O gerador faz o mesmo, e as peças são **trechos reais de 60 pregões** (uns três meses) da bolsa brasileira desde 2000.

Para cada trimestre do futuro, ele sorteia um trimestre do passado e repete os movimentos diários daquele trecho a partir do último preço real. Se o trecho sorteado for o fim de 2008, o futuro terá uma crise com a forma da de 2008, partindo dos preços de hoje.

O **mesmo trecho vale para todos os ativos e indicadores no mesmo dia**. É isso que faz os bancos caírem juntos numa crise bancária, a SELIC subir quando a inflação aperta e a bolsa sentir o juro alto: tudo vem do mesmo momento real.

Na estatística, isso se chama **bootstrap em blocos** (Künsch, 1989): reamostrar um histórico em pedaços contínuos, e não dia a dia, para preservar o que acontece ao longo de semanas.

**Por que não uma fórmula ou ruído?** Os geradores de terreno dos jogos (ruído de Perlin, ondas de seno) e o modelo clássico de finanças (o passeio aleatório com volatilidade constante) produzem curvas contínuas e bem-comportadas. A bolsa não é assim: fica meses parada e despenca 40% em duas semanas, e um dia ruim costuma vir seguido de outros. Medido, o passeio aleatório não teve nenhum dia brusco nem nenhum ativo andando junto com outro. As peças reais trazem tudo isso de graça.

---

## Os biomas: calmo, normal e agitado

Cada trecho do histórico tem um **bioma**, pela agitação do Ibovespa nele: o terço mais calmo, o do meio e o terço mais agitado. Como num mapa de jogo em que depois de deserto vem mais deserto ou savana, e raramente geleira, o bioma do próximo trecho depende do anterior, com as chances medidas no histórico:

| Depois de um trimestre… | calmo | normal | agitado |
| --- | --- | --- | --- |
| **calmo** | 58% | 26% | 16% |
| **normal** | 36% | 43% | 21% |
| **agitado** | 8% | 31% | 61% |

Crise tende a vir seguida de crise (61%), e a calmaria volta aos poucos. Na estatística, isso é um **modelo de troca de regimes** (Hamilton, 1989).

O futuro começa no bioma em que o mercado real está hoje, ou no que você escolher. Começar numa crise dá uma crise que dura e sai aos poucos, como as do histórico.

---

## O encaixe de nível

Peça de mapa tem borda, e a borda precisa casar com a vizinha. Aqui a "borda" é o **estado da economia**: a SELIC, a inflação dos últimos 12 meses e se a inflação está acelerando ou freando. Entre os trechos do bioma sorteado, o gerador prefere os que começam num estado parecido com o do ponto em que o futuro está.

Sem o encaixe, um trimestre de 2015 (inflação de 10%) podia cair num momento de SELIC a 6%, uma combinação que quase não aconteceu. Com ele, juro e inflação seguem coerentes, e a SELIC reage à inflação como o Banco Central reage: a inflação sobe e o juro sobe nos meses seguintes.

Na estatística, isso é o **bootstrap do vizinho mais próximo** (Lall e Sharma, 1996): o próximo pedaço é sorteado entre os que começam mais parecidos com o fim do anterior.

---

## Os controles da geração

Os controles ficam no diálogo "Gerar dados futuros" da [Central de dados](./importacao-ativos.md#gerar-dados-futuros), à esquerda; a prévia fica à direita.

**Semente.** Um número que fixa o sorteio. A mesma semente com os mesmos controles gera sempre o mesmo futuro, e outra semente gera outro futuro igualmente plausível.

**Temperatura**, de 0 a 3, padrão 1. Como a temperatura de uma IA que escreve texto: em 1, o sorteio respeita o histórico como foi; abaixo de 1, favorece trechos calmos; acima, favorece os agitados. A tabela mostra o que cada valor produz em 100 futuros de 5 anos. "Volatilidade anual" é o quanto o Ibovespa costuma oscilar num ano: 24% quer dizer que um ano típico sobe ou cai uns 24% em torno da média.

| Temperatura | Volatilidade anual (mediana) | Anos com queda de mais de 30% |
| --- | --- | --- |
| 0 | 17% | 5% |
| 1 | 24% | 28% |
| 2 | 43% | 64% |
| 3 | 68% | 96% |

O ano mais agitado desde 2000 foi 2008, com volatilidade de 52%. A temperatura 2 fica perto dele; a 3 é o "modo apocalipse": todo ano é pior que 2008.

**Começar em.** O bioma do primeiro trimestre: o do mercado de hoje (padrão), calmaria, normal ou crise. Começando em crise, a volatilidade do primeiro ano fica em 30%, contra 22% começando normal e 18% calmo.

**Choque de inflação**, de −5 a +20 pontos, padrão 0. Os trechos reais nunca passam do que já aconteceu desde 2000; o choque é o jeito de sair disso. Ele soma pontos à inflação anual, cresce em seis meses e depois perde metade da força a cada ano. A SELIC reage subindo **1,5 vez** o que a inflação subiu. Esse é o **princípio de Taylor** (Taylor, 1993): para conter a inflação, o Banco Central sobe o juro mais do que a inflação subiu, senão o juro descontado da inflação cai e a alta continua. A bolsa sente o juro como sentiu no histórico: em média, o Ibovespa caiu 2,9% no trimestre para cada ponto de alta da SELIC, e cada ação sente na proporção do quanto costuma acompanhar o índice.

| Choque | Inflação de 12 meses no pico | SELIC no pico | Maior queda do Ibovespa em 2 anos |
| --- | --- | --- | --- |
| −5 | 6% | 13% (cai até 6%) | −30% |
| 0 | 7% | 15% | −26% |
| +10 | 14% | 28% | −36% |
| +20 | 22% | 43% | −57% |

Medianas de 50 futuros partindo de outubro de 2026, com a SELIC em 13,65%. No choque negativo, o juro cai e a bolsa sobe primeiro, e depois devolve parte da alta quando o juro volta.

---

## Os indicadores, um por um

- **Ibovespa:** repete os movimentos do trecho sorteado, como uma ação.
- **SELIC:** parte do valor real de hoje e soma as variações do trecho sorteado, sem passar do mínimo e do máximo vistos desde 2000 (1,9% a 26,4% ao ano). O choque soma por cima.
- **CDI:** acompanha a SELIC, com a mesma diferença que os dois tinham no último dia real.
- **IPCA:** a inflação de cada mês é a do mês sorteado. A inflação mensal oscila em torno de uma média e não se acumula como a SELIC; somar variações de IPCA levaria a inflações absurdas. O choque soma por cima.

---

## Casos especiais

**Ação que abriu capital depois do trecho sorteado.** Se o trecho é de 2008 e a ação só existe desde 2020, ela segue o movimento das ações do mesmo segmento naquele dia (ou do setor, ou do Ibovespa), na proporção do quanto costuma acompanhá-las, mais uma variação própria sorteada do histórico dela.

**Erro de dado da fonte.** Alguns ativos têm, no histórico baixado, dias em que o preço vai a quase zero e volta no dia seguinte. Uma alta acima de 100% ou uma queda abaixo de 50% num dia é tratada como dia sem pregão, para o erro não ser copiado para o futuro.

**Abertura, máxima, mínima e volume** vêm do mesmo dia real sorteado, como proporção do fechamento e do volume típico do ativo naquela época.

---

## Quão realista é

Para cada critério, o histórico real (2000 a 2026, 37 ações e fundos imobiliários de 10 setores) comparado com 100 futuros gerados, com temperatura 1 e sem choque.

**Dias bruscos (curtose).** Mede o quanto aparecem dias extremos, como um −10% num pregão. Vale 0 numa curva em forma de sino perfeita, em que esses dias praticamente não existem; quanto maior, mais dias bruscos. Real: 53. Gerado: 23. Passeio aleatório: 0. Parte do 53 real ainda é erro de dado da fonte.

**Memória da agitação.** Correlação entre o tamanho do movimento de hoje e o de daqui a 20 pregões: 0 quer dizer que um dia agitado não diz nada sobre o mês seguinte. Real: 0,08. Gerado: 0,07. Passeio aleatório: 0.

**Ativos andando juntos.** Correlação média entre os retornos diários de dois ativos: 1 é andar idêntico, 0 é não ter relação. A tela de [Correlação entre Ativos](./correlacao.md) explica a leitura. Real: 0,38 entre ativos do mesmo setor e 0,25 entre setores diferentes. Gerado: 0,35 e 0,20.

**Queda máxima no ano.** A maior queda do Ibovespa de um pico até o fundo dentro de um ano. Real: mediana de −20%, pior ano −60% (2008), e queda acima de 30% em 6 de 26 anos (23%). Gerado: −20%, pior −71%, e 28% de 500 anos.

**Indicadores reagindo uns aos outros** (por trimestre; real em 309 meses desde 2001):

| Relação | Real | Gerado |
| --- | --- | --- |
| A inflação acelera e a SELIC sobe no trimestre seguinte | 0,37 | 0,33 |
| A SELIC sobe e o Ibovespa cai no mesmo trimestre | −0,31 | −0,24 |
| Meses com juro abaixo da inflação | 6% | 4% |
| Inflação de 12 meses (do 5º ao 95º futuro) | 2,9% a 11,0% | 2,9% a 10,1% |

Uma correlação de 0,37 é uma tendência moderada, não uma regra: em 2008 a SELIC caiu e a bolsa despencou junto, porque a crise derrubou os dois. Por isso o gerador copia as relações dos trechos reais em vez de impor uma regra fixa.

**Teste fora da amostra.** O teste mais duro: gerar 2020 a 2024 usando só o histórico até 2019 e ver se o que aconteceu de verdade cai dentro da faixa dos 100 futuros (do 5º ao 95º pior). O ideal é cair dentro em cerca de 90% das séries. Caiu em 23 de 36 séries no retorno e em 26 de 36 na queda máxima. O ciclo de 2020 a 2022, com a SELIC a 2% e depois a alta mais rápida desde o Plano Real, ficou fora de todos os futuros, porque nada parecido existia no histórico até 2019.

---

## Limites

- **Sem choque, o futuro nunca traz um tipo de crise que não aconteceu desde 2000.** Uma pandemia ou um ciclo de juros inédito só aparece se você pedir, pela temperatura ou pelo choque.
- **Não acerta o destino de uma empresa.** O gerador reproduz a estrutura do mercado (crises, setores, juros), não as surpresas de uma empresa específica, como um escândalo contábil.
- **Os futuros partem do momento atual** e são coerentes com ele, o que também os deixa mais parecidos entre si do que o futuro real costuma ser.

---

## Referências

- Künsch, H. R. (1989). *The jackknife and the bootstrap for general stationary observations*. The Annals of Statistics, 17(3), 1217–1241. Bootstrap em blocos.
- Hamilton, J. D. (1989). *A new approach to the economic analysis of nonstationary time series and the business cycle*. Econometrica, 57(2), 357–384. Troca de regimes.
- Lall, U.; Sharma, A. (1996). *A nearest neighbor bootstrap for resampling hydrologic time series*. Water Resources Research, 32(3), 679–693. Bootstrap do vizinho mais próximo.
- Taylor, J. B. (1993). *Discretion versus policy rules in practice*. Carnegie-Rochester Conference Series on Public Policy, 39, 195–214. Princípio de Taylor.
