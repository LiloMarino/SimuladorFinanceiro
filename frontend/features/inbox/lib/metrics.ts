import type { MetricInfo } from "@/shared/lib/metric-info";
import { displaySignedPercent } from "@/shared/lib/utils/display";

const signedPercent = (value: string | number) => displaySignedPercent(value);

export const MONTH_RETURN: MetricInfo = {
  label: "Sua rentabilidade",
  description: "Quanto os seus investimentos renderam no mês, sem contar aportes",
  definition:
    "A variação da cota no mês: só o que os investimentos renderam move a conta. O aporte, o salário e a despesa entram como capital, não como ganho nem perda.",
  example: "Ex.: começou o mês com R$ 10.000, rendeu R$ 100 e aportou R$ 500 → +1%, e não +6%.",
  reading: "Compare com o CDI e o Ibovespa ao lado: acima deles, você bateu a renda fixa e a bolsa no mês.",
  format: signedPercent,
};

export const MONTH_CDI: MetricInfo = {
  label: "CDI",
  description: "O que a renda fixa sem risco rendeu no mesmo mês",
  definition: "Quanto um título que paga 100% do CDI rendeu nos mesmos pregões do mês.",
  example: "Ex.: CDI de 12% ao ano rende perto de 0,95% num mês.",
  reading: "É a régua mínima: rendendo menos que o CDI, deixar o dinheiro num CDB teria sido melhor.",
  format: signedPercent,
};

export const MONTH_IBOV: MetricInfo = {
  label: "Ibovespa",
  description: "Quanto a bolsa andou no mesmo mês",
  definition: "A variação do índice das maiores ações da bolsa entre o fim do mês anterior e o fim deste.",
  example: "Ex.: o índice foi de 100.000 para 98.000 pontos → −2%.",
  reading: "Acima dele, a sua carteira foi melhor que comprar a bolsa inteira; num mês só, a sorte pesa muito.",
  format: signedPercent,
};

export const POSITION_RESULT: MetricInfo = {
  label: "Resultado da posição",
  description: "O que cada ativo da carteira rendeu no mês",
  definition:
    "O valor do ativo no fim do mês, menos o valor no início, menos o que você comprou, mais o que vendeu. O percentual é sobre o valor do início mais as compras do mês.",
  example: "Ex.: tinha R$ 210 em PETR4, comprou mais R$ 110 e terminou com R$ 375 → ganhou R$ 55, +17,2%.",
  reading: "A melhor e a pior posição mostram o que puxou o mês para cima e para baixo.",
  format: signedPercent,
};

export const YEAR_RETURN: MetricInfo = {
  ...MONTH_RETURN,
  description: "Quanto os seus investimentos renderam no ano, sem contar aportes",
  definition:
    "As rentabilidades de cada mês jogado no ano, compostas: um mês rende sobre o resultado do anterior. Aportes não contam como ganho.",
  example: "Ex.: +10% num mês e −5% no seguinte → 1,10 × 0,95 = +4,5% no período.",
};
