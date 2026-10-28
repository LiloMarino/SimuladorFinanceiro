import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayMoneyWhole, displayPercent } from "@/shared/lib/utils/display";

export const INTENTION: MetricInfo = {
  label: "Intenção de voto",
  description: "De cada 100 eleitores, quantos votariam no partido, pela última pesquisa",
  definition:
    "Cada grupo de eleitores vota pelo saldo de cada partido (apoio menos rejeição); o total soma os grupos pelo tamanho de cada um. Quem não escolheu ninguém fica como indeciso.",
  example: "Ex.: UPR com 33, FDS com 32 e PRL com 23 somam 88; os outros 12 são indecisos.",
  reading:
    "Mais pontos, mais perto de vencer. A pesquisa sai todo dia 1º e traz a margem de erro; a conta da eleição ignora os indecisos e usa só os votos válidos.",
  format: (value) => Number(value).toLocaleString("pt-BR", { maximumFractionDigits: 1 }),
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
    "Os dois partidos com mais pontos disputam. Em cada grupo, os eleitores de quem saiu se dividem entre os finalistas e os indecisos na mesma proporção em que o grupo já está; os indecisos não votam.",
  example:
    "Ex.: entre os aposentados, PRL 46, UPR 24 e indecisos 13; os 17 do FDS, que saiu, vão 46 : 24 : 13 para PRL, UPR e indecisos.",
  reading:
    "Quem somar mais votos válidos vence. É só uma projeção feita com a última pesquisa: ela muda a cada mês, e as doações entre os turnos também mexem.",
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

export const VOTE_YIELD: MetricInfo = {
  label: "Quanto a verba rende",
  description: "Pontos de apoio ganhos por mês, em cada grupo",
  definition:
    "A raiz quadrada do gasto mensal, dividida por 64, somada ao apoio do partido em todos os seis grupos. A curva sobe rápido no começo e achata: dobrar a verba não dobra o apoio.",
  example: "Ex.: R$ 8.000 por mês rendem 1,4 ponto de apoio; R$ 16.000 rendem 2,0 pontos, não 2,8.",
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

const points = (value: string | number) => Number(value).toLocaleString("pt-BR", { maximumFractionDigits: 0 });

export const AFFINITY: MetricInfo = {
  label: "Afinidade",
  description: "Quanto o que o grupo quer se parece com o perfil do partido",
  definition:
    "O ponto de partida do apoio, de 0 a 100. Todo partido parte de 20 em cada grupo; cada bandeira soma ou tira conforme o grupo quer aquele valor.",
  example:
    "Ex.: os investidores querem muito Mercado livre (+12) e um pouco Estabilidade (+6) e Proteção ao poupador (+6): um partido com as três parte de 20 + 24 = 44 com eles.",
  reading:
    "Acima de 40 o grupo já começa simpático; perto de zero, ele quase não considera o partido. O perfil se move com as medidas aprovadas no governo, e a afinidade vai junto.",
  format: points,
};

export const SUPPORT: MetricInfo = {
  label: "Apoio",
  description: "O quanto o grupo gosta do partido, de 0 a 100",
  definition: "A afinidade com as bandeiras mais o que a campanha somou no grupo. Sobe com a verba gasta todo mês.",
  example: "Ex.: afinidade 44 e 12 pontos de campanha → apoio 56 entre os investidores.",
  reading: "Acima de 50 é base firme; abaixo de 20, o grupo mal considera o partido.",
  format: points,
};

export const REJECTION: MetricInfo = {
  label: "Rejeição",
  description: "O quanto o grupo não vota no partido de jeito nenhum, de 0 a 100",
  definition:
    "Sobe com promessa descumprida ao grupo e com mês de governo reprovado por ele. Não cai com o tempo: só com reparação, como cumprir uma promessa ao grupo.",
  example: "Ex.: apoio 18 e rejeição 41 entre os servidores → saldo −23: o partido não leva voto ali.",
  reading: "Zero é o melhor. Rejeição maior que o apoio zera o voto do grupo no partido.",
  format: points,
};

export const BALANCE: MetricInfo = {
  label: "Saldo",
  description: "Apoio menos rejeição: é dele que sai o voto do grupo",
  definition:
    "Em cada grupo, a fatia de cada partido é proporcional ao saldo positivo dele; os indecisos entram como se fossem um partido de saldo 15.",
  example: "Ex.: dois partidos com saldo 30 e 25 → 43% e 36% do grupo; os outros 21% (15 ÷ 70) ficam indecisos.",
  reading: "Saldo maior, fatia maior do grupo. Saldo zero ou negativo não leva voto nenhum ali.",
  format: points,
};

export const POLL_MARGIN: MetricInfo = {
  label: "Margem de erro",
  description: "A faixa onde o número real está",
  definition:
    "A pesquisa ouve uma amostra, não o eleitorado inteiro: cada número sai com um erro sorteado dentro da margem. Grupo menor tem amostra menor e margem maior.",
  example: "Ex.: “30%, com margem de 3 pontos para mais ou para menos” quer dizer que o real está entre 27% e 33%.",
  reading:
    "Quando as faixas de dois partidos se cobrem (a diferença é de até duas margens), é empate técnico: a pesquisa não diz quem está na frente.",
  format: (value) => `±${points(value)}`,
};
