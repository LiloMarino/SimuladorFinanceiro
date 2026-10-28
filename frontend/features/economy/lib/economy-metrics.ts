import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayPercent } from "@/shared/lib/utils/display";

const percent = (value: string | number) => displayPercent(value, 2);

export const SELIC: MetricInfo = {
  label: "SELIC",
  description: "O juro básico da economia, ao ano",
  definition:
    "A taxa que o Banco Central fixa e que serve de base para todos os outros juros: o CDI, os títulos do Tesouro, o crédito. Ela só muda nas reuniões do Copom.",
  example: "Ex.: com a SELIC a 10% ao ano, R$ 100 parados nela viram R$ 110 em um ano.",
  reading:
    "Quanto mais alta, mais a renda fixa rende e mais caro fica o crédito. O Copom costuma subi-la quando a inflação passa da meta e baixá-la quando a inflação cede.",
  format: percent,
};

export const IPCA: MetricInfo = {
  label: "IPCA em 12 meses",
  description: "A inflação oficial, acumulada no último ano",
  definition: "O quanto os preços subiram nos últimos 12 meses, medido pelo índice oficial do país.",
  example: "Ex.: 5% em 12 meses quer dizer que o que custava R$ 100 há um ano custa R$ 105 hoje.",
  reading:
    "Dentro da meta do ano é o bom sinal; acima dela, o dinheiro perde poder de compra e o governo perde aprovação.",
  format: percent,
};

export const REAL_RATE: MetricInfo = {
  label: "Juro real",
  description: "Quanto o dinheiro rende de verdade, descontada a inflação",
  definition: "A SELIC menos o IPCA de 12 meses: o rendimento que sobra depois de a inflação comer parte dele.",
  example: "Ex.: SELIC de 10% com inflação de 4% dá juro real de 6%; R$ 100 viram R$ 106 em poder de compra.",
  reading:
    "Positivo, guardar dinheiro na renda fixa ganha da inflação; negativo, perde. Acima de uns 7% esfria a economia; perto de zero ou negativo, aquece e puxa a inflação.",
  format: percent,
};
