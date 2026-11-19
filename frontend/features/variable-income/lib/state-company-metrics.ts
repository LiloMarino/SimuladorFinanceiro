import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";

export const STATE_FAIR_VALUE: MetricInfo = {
  label: "Valor justo",
  description: "O que o lucro esperado vale hoje",
  definition: "Quanto vale hoje o lucro que se espera da estatal nos próximos anos. O preço do dia anda em volta dele.",
  example:
    "Valor justo de R$ 25,10 e preço de R$ 24,37: a ação está 2,9% abaixo. Se o PIB do ano vem acima da média, o valor justo sobe mais rápido.",
  reading: "Preço abaixo do valor justo é ação barata pelo lucro; acima, cara.",
  format: (value) => displayMoney(value),
};

export const STATE_DIVIDENDS: MetricInfo = {
  label: "Dividendos por ação",
  description: "O que a estatal pagou para cada ação",
  definition: "Quanto a estatal pagou para cada ação no período, somando os meses.",
  example: "R$ 0,87 em 8 meses sobre um preço de R$ 24,37: 3,6%. Quem tem 2.000 ações recebeu R$ 1.740.",
  reading: "Compare com o juro da renda fixa no mesmo período: abaixo dele, o retorno precisa vir do preço.",
  format: (value) => displayMoney(value),
};

export const STATE_DIVIDEND_POLICY: MetricInfo = {
  label: "Política de dividendos",
  description: "A parte do lucro do mês que vira dividendo",
  definition: "A parte do lucro do mês que vira dividendo. O presidente escolhe entre três.",
  example: "Lucro de R$ 0,24 por ação: Reinvestir paga R$ 0,06, Normal R$ 0,12 e Espremer R$ 0,19.",
  reading: "Reinvestir paga menos agora e faz a estatal crescer; Espremer paga mais agora e a encolhe.",
  format: (value) => displayPercent(value, 0),
};

export const STATE_BETA: MetricInfo = {
  label: "β (beta) · sensibilidade à bolsa",
  description: "Quanto o preço anda quando a bolsa anda",
  definition: "Quanto o preço anda quando a bolsa inteira anda no mesmo dia.",
  example: "Com β 0,8: a bolsa cai 2% e a estatal cai 1,6%; a bolsa sobe 5% e ela sobe 4%.",
  reading: "Abaixo de 1, oscila menos que a bolsa; acima de 1, mais. Estatal costuma ficar abaixo.",
  format: (value) => `${value}`,
};
