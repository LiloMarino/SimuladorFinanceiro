import type { MetricInfo } from "@/shared/lib/metric-info";
import { signedIpca } from "@/shared/lib/effects";
import { displayPercent } from "@/shared/lib/utils/display";

export const APPROVAL: MetricInfo = {
  label: "Aprovação",
  description: "De cada 100 eleitores, quantos aprovam o governo",
  definition:
    "É a média da satisfação dos 6 grupos de eleitores, pesada pelo tamanho de cada um. Cada grupo anda um terço do caminho até o alvo dele a cada fim de mês, e o alvo sai do que o grupo lê: inflação, SELIC, bolsa, desemprego, prêmio de risco da dívida e as medidas do governo.",
  example:
    "Ex.: se os grupos que somam 60% do eleitorado estão em 70 e os outros 40% estão em 40, a aprovação geral é 0,6 × 70 + 0,4 × 40 = 58.",
  reading:
    "Acima de 50, o governo tem folga. Abaixo de 25 por 6 fechamentos seguidos, depois do primeiro ano, abre o pedido de impeachment, que a casa vota. A leitura vale para o mês: a aprovação se mede de novo no fechamento de cada mês.",
  format: (value) => `${value}%`,
};

export const SATISFACTION: MetricInfo = {
  label: "Satisfação",
  description: "De cada 100 pessoas do grupo, quantas aprovam o governo",
  definition:
    "A fatia do grupo que aprova o governo hoje. Na posse, cada grupo começa na proporção em que votou no presidente no turno que decidiu a eleição.",
  example: "Ex.: aposentados em 37 significa que 37 de cada 100 aposentados aprovam o governo.",
  reading:
    "Acima de 55, o grupo aprova o mês e o apoio ao partido do presidente sobe nele; abaixo de 45, reprova e a rejeição sobe. Entre os dois, fica neutro e nada muda.",
  format: (value) => `${value}`,
};

export const TARGET: MetricInfo = {
  label: "Alvo",
  description: "Onde a satisfação do grupo para se nada mudar",
  definition:
    "Sai do que o grupo lê (inflação, SELIC, bolsa, desemprego e prêmio de risco da dívida) e das medidas que valem. A satisfação anda um terço do caminho até o alvo a cada fim de mês.",
  example: "Ex.: com satisfação 40 e alvo 70, o grupo vai a 50 no próximo fechamento, depois a 57 e a 61.",
  reading: "Alvo acima da satisfação: o grupo está melhorando. Abaixo: está piorando, mesmo que hoje ainda aprove.",
  format: (value) => `${value}`,
};

export const FORECAST: MetricInfo = {
  label: "Placar previsto",
  description: "Quantos votos Sim a medida deve ter, em faixa",
  definition:
    "Soma os votos Sim se cada bancada seguir a orientação, menos os deputados que podem votar contra porque a medida contraria quem elegeu a bancada. A faixa vai do pior caso (todos os que podem desobedecer votam contra) ao melhor (ninguém desobedece).",
  example:
    "Ex.: Sim 53 a 60 significa 60 votos se ninguém desobedecer e 53 se todos os 7 que podem desobedecer votarem Não.",
  reading:
    "A medida passa com 51 votos ou mais, de 101. Faixa toda acima de 51: passa. Toda abaixo: cai. Atravessando o 51: depende de quem desobedecer.",
  format: (value) => `${value}`,
};

export const DEFIANCE: MetricInfo = {
  label: "Pode desobedecer",
  description: "Deputados que podem votar contra a orientação do líder",
  definition:
    "Cada deputado é sorteado na votação. A chance de votar contra cresce com o quanto os eleitores da bancada querem o voto oposto ao orientado, e nunca passa de um terço da bancada.",
  example:
    "Ex.: os investidores são 40% de quem elegeu o MRC e perdem com a medida. Se o MRC orientar Sim, até 4 dos 16 deputados podem votar Não.",
  reading:
    "Quanto menor, mais a bancada é previsível: 0 significa que ela vota como o líder orientou. Um terço da bancada é o máximo.",
  format: (value) => `${value}`,
};

export const WITH_GOVERNMENT: MetricInfo = {
  label: "Com o governo",
  description: "Em quantos por cento das votações a bancada votou Sim",
  definition:
    "Entre as medidas que o presidente já levou à casa, a fatia dos deputados da bancada que votou Sim. Vem sempre com o número de votações: 100% de 2 votações pesa menos que 80% de 12.",
  example: "Ex.: 75% em 8 votações: de cada 4 votos da bancada, 3 foram Sim.",
  reading:
    "Perto de 100%, a bancada é da base do governo; perto de 0%, é da oposição. Com poucas votações o número ainda varia muito.",
  format: (value) => `${value}%`,
};

export const DEFECTION_RATE: MetricInfo = {
  label: "Desobediência",
  description: "Dos deputados da bancada, quantos por cento votaram contra o líder",
  definition: "Média, nas votações já feitas, dos deputados da bancada que votaram contra a orientação do líder.",
  example: "Ex.: 6% em 8 votações: de cada 100 votos da bancada, 6 foram contra o líder.",
  reading:
    "Perto de 0%, o líder manda na bancada. Acima de 15%, ele orienta contra o que os eleitores da bancada querem, com frequência.",
  format: (value) => `${value}%`,
};

export const BARRIER: MetricInfo = {
  label: "Barreira de 5%",
  description: "O mínimo de votos válidos para ter cadeira",
  definition:
    "O partido que não alcança 5% dos votos válidos da eleição da casa fica sem cadeira, e os votos dele não entram na divisão.",
  example: "Ex.: com 4,2% dos votos, o partido fica de fora; com 5,3%, entra e leva umas 5 cadeiras de 101.",
  reading: "Partido pequeno precisa passar da barreira antes de pensar em bancada.",
  format: (value) => `${value}%`,
};

export const DHONDT: MetricInfo = {
  label: "Como os votos viram cadeiras",
  description: "O método D'Hondt, que divide as 101 cadeiras",
  definition:
    "Os votos de cada partido são divididos por 1, 2, 3 e assim por diante. As 101 maiores divisões levam uma cadeira cada, então a cadeira seguinte de um partido sempre vale menos votos que a anterior.",
  example:
    "Ex.: com 40, 35 e 25 votos, o primeiro partido leva a 1ª cadeira (40), o segundo a 2ª (35), o terceiro a 3ª (25), e a 4ª volta ao primeiro (40÷2 = 20)... até as 101 saírem.",
  reading:
    "O partido maior leva uma fatia de cadeiras um pouco acima da fatia de votos; os pequenos ficam um pouco abaixo.",
  format: (value) => `${value}`,
};

export const REVENUE: MetricInfo = {
  label: "Receita",
  description: "O que o governo arrecada no país em um ano",
  definition:
    "Tudo o que o governo recebe em impostos, medido em % do PIB por ano. Os impostos do jogo (ações, day trade, renda fixa) são uma fatia pequena; o resto da arrecadação do país é fixo. O IR que os jogadores pagam não entra: as operações da sala são pequenas perto do país.",
  example: "Ex.: 18,38% de um PIB de R$ 7,4 tri são R$ 1,36 tri por ano, ou uns R$ 113 bi por mês.",
  reading:
    "Mexer na alíquota muda a receita, mas menos que proporcionalmente: quem paga menos passa a operar mais. Receita acima do gasto sobra e a dívida cai; abaixo, falta e a dívida sobe.",
  format: (value) => displayPercent(value, 2),
};

export const PRIMARY_RESULT: MetricInfo = {
  label: "Resultado primário",
  description: "Receita menos gasto, sem contar os juros da dívida",
  definition:
    "O que sobra (superávit) ou falta (déficit) depois de o governo pagar suas despesas, antes de pagar os juros da dívida. As medidas de imposto mexem aqui.",
  example: "Ex.: receita de R$ 113,3 bi e gasto de R$ 113,5 bi no mês dão primário de −R$ 0,2 bi: faltou um pouco.",
  reading:
    "Positivo é bom: sobra dinheiro para a dívida cair. Negativo por muito tempo faz a dívida subir, e o prêmio de risco junto.",
  format: (value) => displayPercent(value, 2),
};

export const INTEREST: MetricInfo = {
  label: "Juros da dívida",
  description: "Quanto o governo paga só para carregar a dívida",
  definition:
    "A dívida vezes o juro que ela paga: a SELIC mais o prêmio de risco. Sai da conta todo mês, mesmo que o governo não gaste nada de novo.",
  example: "Ex.: dívida de 77,8% do PIB com juro de 5,7% ao ano custa 4,4% do PIB por ano em juros.",
  reading:
    "Quanto menor, melhor. SELIC alta e dívida alta se somam, e o prêmio faz o juro subir justamente quando a dívida cresce.",
  format: (value) => displayPercent(value, 2),
};

export const RESULT: MetricInfo = {
  label: "Resultado",
  description: "O que sobra ou falta depois de pagar os juros",
  definition:
    "O resultado primário menos os juros da dívida. Se for negativo (déficit), o governo se endivida para fechar o mês, e o déficit vira dívida.",
  example: "Ex.: −R$ 0,1 bi de primário e −R$ 27,1 bi de juros dão resultado de −R$ 27,2 bi no mês.",
  reading:
    "Positivo, a dívida cai. Negativo, a dívida sobe, mas a economia crescendo também faz a dívida pesar menos no PIB.",
  format: (value) => displayPercent(value, 2),
};

export const QUEUE_BUDGET: MetricInfo = {
  label: "No orçamento",
  description: "Quanto a medida muda o resultado do governo",
  definition:
    "A variação do resultado do governo (receita menos gasto) que a medida causa, em % do PIB por ano. Verde melhora o resultado: imposto que arrecada mais ou gasto que cai. Vermelho piora: imposto que arrecada menos ou gasto que sobe. É uma estimativa: supõe a medida valendo e mais nada mudando.",
  example:
    "Ex.: −0,08% quer dizer que o governo passa a faltar 0,08% do PIB a mais por ano, uns R$ 5,9 bi num PIB de R$ 7,4 tri.",
  reading:
    "Resultado pior aumenta o déficit e a dívida; melhor, o contrário. Medida de poucos centésimos quase não pesa na conta do país.",
  format: (value) => displayPercent(value, 2),
};

export const QUEUE_INFLATION: MetricInfo = {
  label: "Na inflação",
  description: "Pontos que a medida soma ao IPCA de 12 meses, no pico",
  definition:
    "Só as medidas de gasto mexem aqui. O IPCA de 12 meses é a inflação acumulada no último ano; a medida soma ou tira pontos dele. O efeito demora: enche em 6 meses, vale cheio no pico e cai pela metade a cada 12 meses. Vermelho é inflação a mais; verde, a menos.",
  example: "Ex.: +0,25 com o IPCA em 3,3% leva o 12 meses a 3,55% no pico, uns 6 meses depois de a medida valer.",
  reading:
    "Inflação a mais desagrada quem lê a inflação, e o Banco Central sobe a SELIC 1,5 vez o tanto. Abaixo de 0,1 ponto quase não se sente.",
  format: (value) => `${signedIpca(value)} ponto`,
};

export const INFLATION_EXPECTED: MetricInfo = {
  label: "Inflação esperada",
  description: "Quanto a medida muda o IPCA de 12 meses, no pico",
  definition:
    "A medida de gasto põe mais (ou menos) dinheiro nas mãos de quem consome, e os preços reagem meses depois. O efeito enche em 6 meses, vale cheio no pico e cai pela metade a cada 12 meses. Vale para a partida inteira, na história e no futuro gerado, e a série guardada não muda: a diferença aparece tracejada no painel da economia.",
  example:
    "Ex.: +0,55 ponto com o IPCA em 3,3% leva o 12 meses a 3,85% no pico. Se o Banco Central responde com 1,5 vez o tanto, a SELIC sobe 0,83 ponto.",
  reading:
    "Pontos a mais pesam contra o governo: os grupos que leem a inflação reprovam, a SELIC sobe e a bolsa cai. Menos de 0,1 ponto quase não se sente.",
  format: (value) => `${signedIpca(value)} ponto`,
};

export const SPENDING_COST: MetricInfo = {
  label: "Custa",
  description: "Quanto a medida pesa no gasto do governo, por ano",
  definition:
    "A parte do gasto do governo que a medida ocupa hoje, em % do PIB por ano e em reais por ano. No reajuste, é a folha de pagamento que ele multiplica, e ela cresce todo janeiro.",
  example: "Ex.: 1,40% de um PIB de R$ 7,4 tri são uns R$ 104 bi por ano.",
  reading:
    "Gasto maior que a receita aumenta o déficit e a dívida. O que a medida custa não diz se vale a pena: pese também o que ela faz com a inflação e com os grupos de eleitores.",
  format: (value) => displayPercent(value, 2),
};

export const SPENDING_INFLATION_NOW: MetricInfo = {
  label: "Na inflação agora",
  description: "Pontos de IPCA que a medida põe hoje",
  definition:
    "O quanto da medida já chegou ao IPCA de 12 meses neste dia. Sobe nos primeiros 6 meses depois de a medida valer, fica cheio no pico e cai pela metade a cada 12 meses.",
  example: "Ex.: +0,12 hoje e +0,25 no pico: a medida ainda está chegando e vai pesar mais nos próximos meses.",
  reading: "Zero ou traço: o efeito ainda não começou ou já sumiu. Vermelho é inflação a mais; verde, a menos.",
  format: (value) => `${signedIpca(value)} ponto`,
};
