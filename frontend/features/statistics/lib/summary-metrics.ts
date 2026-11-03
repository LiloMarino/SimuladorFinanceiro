import type { MetricInfo } from "@/shared/lib/metric-info";
import { displaySignedPercent } from "@/shared/lib/utils/display";

const signedPercent = (value: string | number) => displaySignedPercent(value);

export const YEAR_RETURN: MetricInfo = {
  label: "Sua rentabilidade",
  description: "Quanto os seus investimentos renderam no ano, sem contar aportes",
  definition:
    "As rentabilidades de cada mês jogado no ano, compostas: um mês rende sobre o resultado do anterior. Aportes não contam como ganho.",
  example: "Ex.: +10% num mês e −5% no seguinte → 1,10 × 0,95 = +4,5% no período.",
  reading: "Compare com o CDI e o Ibovespa ao lado: acima deles, você bateu a renda fixa e a bolsa no ano.",
  format: signedPercent,
};

export const YEAR_CDI: MetricInfo = {
  label: "CDI",
  description: "O que a renda fixa sem risco rendeu no mesmo ano",
  definition: "Quanto um título que paga 100% do CDI rendeu nos mesmos pregões do ano.",
  example: "Ex.: CDI de 12% ao ano rende 12% em doze meses.",
  reading: "É a régua mínima: rendendo menos que o CDI, deixar o dinheiro num CDB teria sido melhor.",
  format: signedPercent,
};

export const YEAR_IBOV: MetricInfo = {
  label: "Ibovespa",
  description: "Quanto a bolsa andou no mesmo ano",
  definition: "A variação do índice das maiores ações da bolsa entre o fim do ano anterior e o fim deste.",
  example: "Ex.: o índice foi de 100.000 para 110.000 pontos → +10%.",
  reading: "Acima dele, a sua carteira foi melhor que comprar a bolsa inteira.",
  format: signedPercent,
};
