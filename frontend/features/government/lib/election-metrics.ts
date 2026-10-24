import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayMoneyWhole, displayPercent } from "@/shared/lib/utils/display";

export const INTENTION: MetricInfo = {
  label: "Intenção de voto",
  description: "De cada 100 eleitores, quantos votariam no partido hoje",
  definition:
    "Pontos de apoio de cada partido. Cada ponto é um eleitor em cada 100; quem não escolheu ninguém fica como indeciso.",
  example:
    "Ex.: UPR com 33, FDS com 32 e PRL com 23 somam 88; os outros 12 são indecisos.",
  reading:
    "Mais pontos, mais perto de vencer. A conta da eleição ignora os indecisos: ela usa só os votos válidos.",
  format: (value) => `${Number(value).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}`,
};

export const VALID_SHARE: MetricInfo = {
  label: "Votos válidos",
  description: "A fatia de cada partido entre quem já escolheu",
  definition: "Os pontos do partido divididos pela soma dos pontos de todos os partidos, sem contar os indecisos.",
  example: "Ex.: 33 de 88 pontos válidos → 37,5% (33 ÷ 88).",
  reading:
    "Passou de 50% dos válidos, vence já no 1º turno. Se ninguém passa, os dois primeiros vão ao 2º turno. Nunca confunda com o total de eleitores: a base são só os votos válidos.",
  format: (value) => displayPercent(value, 1),
};

export const RUNOFF: MetricInfo = {
  label: "Simulação do 2º turno",
  description: "Como seria o 2º turno se fosse hoje",
  definition:
    "Os dois partidos com mais pontos disputam. Os eleitores de cada partido que ficou de fora vão para o finalista com a promessa mais parecida com a do partido deles.",
  example:
    "Ex.: o PRL (promessa 2) saiu; o FDS (promessa 3) está mais perto do que o UPR (promessa 5), então os 23 pontos do PRL vão para o FDS.",
  reading: "Quem somar mais pontos vence. É só uma projeção: a pesquisa muda a cada mês e as doações entre os turnos também mexem.",
  format: (value) => displayPercent(value, 0),
};

export const BUDGET: MetricInfo = {
  label: "Verba por mês",
  description: "A soma das contribuições dos filiados",
  definition:
    "O que o partido gasta em campanha por mês. Cada filiado escolhe quanto contribui, e a parte dele sai do caixa dele no dia 1º.",
  example: "Ex.: Lilo contribui R$ 6.000 e Rafa R$ 2.000 → verba de R$ 8.000 por mês.",
  reading:
    "Verba maior rende mais apoio, mas cada real a mais rende menos que o anterior: o apoio cresce com a raiz quadrada do gasto.",
  format: (value) => displayMoneyWhole(value),
};

export const SPENT: MetricInfo = {
  label: "Gasto até agora",
  description: "O que o partido já gastou na campanha",
  definition: "A soma das verbas mensais já cobradas dos filiados desde que a campanha abriu.",
  example: "Ex.: 6 meses de R$ 8.000 → R$ 48.000 gastos.",
  reading: "É público e não volta: o que saiu do caixa de um filiado virou apoio do partido.",
  format: (value) => displayMoneyWhole(value),
};

export const PROMISE: MetricInfo = {
  label: "Promessa",
  description: "Onde o partido se coloca entre cortar imposto e gastar",
  definition:
    "A faixa de 1 (impostos bem baixos) a 5 (gasto bem alto) em que o partido se posiciona. Ela é escolhida por quem funda e fica pública.",
  example:
    "Ex.: promessa 2 é impostos baixos; promessa 5 é gasto bem alto. Quanto mais perto duas promessas, mais parecidos os partidos.",
  reading:
    "No 2º turno, os eleitores de um partido eliminado vão para o finalista com a promessa mais parecida. Por isso a posição na régua importa tanto quanto a verba.",
  format: (value) => String(value),
};

export const VOTE_YIELD: MetricInfo = {
  label: "Quanto a verba rende",
  description: "Pontos de intenção de voto ganhos por mês",
  definition:
    "A raiz quadrada do gasto mensal, dividida por 64. A curva sobe rápido no começo e achata: dobrar a verba não dobra o apoio.",
  example: "Ex.: R$ 8.000 por mês rendem 1,4 ponto; R$ 16.000 rendem 2,0 pontos, não 2,8.",
  reading:
    "Gastar cedo vale mais: quatro meses de R$ 10.000 rendem 6,25 pontos, enquanto R$ 40.000 de uma vez rendem 3,1.",
  format: (value) => Number(value).toLocaleString("pt-BR", { maximumFractionDigits: 1 }),
};

export const PARTY_NETWORTH: MetricInfo = {
  label: "Patrimônio do partido",
  description: "A soma do patrimônio dos filiados",
  definition: "O patrimônio de cada filiado somado. O partido do computador não entra no ranking.",
  example: "Ex.: Lilo com R$ 412.300 e Rafa com R$ 298.400 → partido com R$ 710.700.",
  reading: "Maior é melhor. Na vitória política, o partido com a maior soma vence a partida.",
  format: (value) => displayMoneyWhole(value),
};
