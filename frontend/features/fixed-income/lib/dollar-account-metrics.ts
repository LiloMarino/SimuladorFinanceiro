import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayDollars, displayPercent } from "@/shared/lib/utils/display";

export const FED_RATE: MetricInfo = {
  label: "Juro do Fed",
  description: "O que a conta rende em dólar, ao ano",
  definition:
    "A taxa de juros básica dos Estados Unidos, que o banco central americano (o Fed) fixa. A conta em dólar rende 100% dela, todo dia útil, e o rendimento cai em dólar, não em reais.",
  example: "Ex.: com o Fed a 5% ao ano, US$ 1.000 viram US$ 1.050 em um ano.",
  reading:
    "Mais alto é melhor para a conta. Mas o que importa para você é o resultado em reais, e ele também depende do dólar: o juro americano costuma ser bem menor que o CDI.",
  format: (value) => `${displayPercent(value)} a.a.`,
};

export const BREAK_EVEN: MetricInfo = {
  label: "Empata se o dólar subir",
  description: "A alta do dólar em 12 meses que iguala a conta ao CDI",
  definition:
    "Quanto o dólar precisa subir em um ano para a conta em dólar render o mesmo que o CDI. É a conta (1 + CDI) ÷ (1 + juro do Fed) − 1: a diferença entre o juro brasileiro e o americano, que o dólar precisa cobrir.",
  example: "Ex.: com CDI de 13% e Fed de 5%, o empate é 7,6%: com o dólar subindo 7,6%, os dois rendem igual.",
  reading:
    "Dólar subindo mais que o empate: a conta ganha do CDI. Subindo menos, ou caindo: o CDI ganha. Quanto menor o número, mais fácil a conta compensar.",
  format: (value) => displayPercent(value, 1),
};

export const DOLLAR_ACCOUNT_TAX: MetricInfo = {
  label: "IR de 15%",
  description: "Sobre o ganho em reais, retido no resgate",
  definition:
    "No resgate o IR é 15% do ganho em reais, que junta o juro do Fed e a alta do dólar. Se o valor em reais está abaixo do que você aplicou, não há IR. Na entrada, o IOF do câmbio de 1,1% sai do valor aplicado.",
  example: "Ex.: R$ 10.000 aplicados viram R$ 11.000: o ganho é R$ 1.000 e o IR é R$ 150.",
  reading: "O IR só incide no resgate, sobre o que realmente ganhou; perda não paga imposto.",
  format: (value) => displayPercent(value, 0),
};

export const DOLLAR_BALANCE: MetricInfo = {
  label: "Saldo em dólar",
  description: "O que você tem na conta, em US$",
  definition:
    "Quantos dólares estão na conta, já com o rendimento do Fed. O valor em reais é esse saldo vezes o dólar de hoje.",
  example: "Ex.: US$ 1.978 a R$ 5,50 valem R$ 10.879.",
  reading: "O saldo em US$ só cresce com o juro; o valor em reais sobe e desce com o dólar.",
  format: (value) => displayDollars(value),
};
