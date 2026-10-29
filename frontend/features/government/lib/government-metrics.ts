import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayPercent } from "@/shared/lib/utils/display";

export const APPROVAL: MetricInfo = {
  label: "Aprovação",
  description: "De cada 100 eleitores, quantos aprovam o governo",
  definition:
    "É a média da satisfação dos 6 grupos de eleitores, pesada pelo tamanho de cada um. Cada grupo anda um terço do caminho até o alvo dele a cada fim de mês, e o alvo sai do que o grupo lê: inflação, SELIC, bolsa, desemprego, prêmio de risco da dívida e as medidas do governo. É também a chance de cada medida passar no Congresso.",
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
    "Sai do que o grupo lê (inflação, SELIC, bolsa, desemprego e prêmio de risco da dívida) e das medidas que valem. A satisfação anda um terço do caminho até o alvo a cada fim de mês.",
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
  description: "Quanto a medida muda a receita do governo",
  definition:
    "A variação da receita que a medida causa, em % do PIB por ano. Verde soma à receita do governo; vermelho tira dela. É uma estimativa: supõe a medida valendo e mais nada mudando.",
  example:
    "Ex.: −0,08% quer dizer que o governo passa a arrecadar 0,08% do PIB a menos por ano, uns R$ 5,9 bi num PIB de R$ 7,4 tri.",
  reading:
    "Receita menor aumenta o déficit e a dívida; maior, o contrário. Medida de poucos centésimos quase não pesa na conta do país.",
  format: (value) => displayPercent(value, 2),
};
