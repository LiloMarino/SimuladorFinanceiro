import type { MetricInfo } from "@/shared/lib/metric-info";

export const APPROVAL: MetricInfo = {
  label: "Aprovação",
  description: "De cada 100 eleitores, quantos aprovam o governo",
  definition:
    "Começa em 50 na posse e se move todo mês: sobe com inflação dentro da meta, bolsa em alta e corte de imposto; cai com inflação alta, bolsa em queda, imposto novo e promessa quebrada. É também a chance de cada medida passar no Congresso.",
  example:
    "Ex.: 50 de base + 4 da inflação + 3 da bolsa − 1 de um imposto novo = 56. Das 100 pessoas, 56 aprovam, e cada medida tem 56% de chance.",
  reading:
    "Acima de 50, o governo tem folga. Abaixo de 25 por 3 meses seguidos, o impeachment tira o presidente. A leitura vale para o mês: a aprovação se mede de novo no fechamento de cada mês.",
  format: (value) => `${value}%`,
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
