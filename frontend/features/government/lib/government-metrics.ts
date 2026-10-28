import type { MetricInfo } from "@/shared/lib/metric-info";

export const APPROVAL: MetricInfo = {
  label: "Aprovação",
  description: "De cada 100 eleitores, quantos aprovam o governo",
  definition:
    "É a média da satisfação dos 6 grupos de eleitores, pesada pelo tamanho de cada um. Cada grupo anda um terço do caminho até o alvo dele a cada fim de mês, e o alvo sai do que o grupo lê: inflação, SELIC, bolsa e as medidas do governo. É também a chance de cada medida passar no Congresso.",
  example:
    "Ex.: se os grupos que somam 60% do eleitorado estão em 70 e os outros 40% estão em 40, a aprovação geral é 0,6 × 70 + 0,4 × 40 = 58.",
  reading:
    "Acima de 50, o governo tem folga. Abaixo de 25 por 6 fechamentos seguidos, depois do primeiro ano, o impeachment tira o presidente. A leitura vale para o mês: a aprovação se mede de novo no fechamento de cada mês.",
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
    "Sai da inflação, da SELIC e da bolsa, pelo que o grupo lê, e das medidas que valem. A satisfação anda um terço do caminho até o alvo a cada fim de mês.",
  example: "Ex.: com satisfação 40 e alvo 70, o grupo vai a 50 no próximo fechamento, depois a 57 e a 61.",
  reading: "Alvo acima da satisfação: o grupo está melhorando. Abaixo: está piorando, mesmo que hoje ainda aprove.",
  format: (value) => `${value}`,
};

export const CHANCE: MetricInfo = {
  label: "Chance",
  description: "A chance de o Congresso aprovar a medida",
  definition:
    "No fechamento do mês, o Congresso vota a fila inteira. Cada medida passa com chance igual à aprovação do governo naquele dia.",
  example:
    "Ex.: com 56% de aprovação, cada medida da fila tem 56% de chance, e o sorteio de uma não decide o das outras.",
  reading:
    "Quanto maior a aprovação, mais fácil passar. A chance só diz a probabilidade: uma medida com 80% ainda pode cair.",
  format: (value) => `${value}%`,
};
