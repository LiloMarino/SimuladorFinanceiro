/** Patrimônio, rendimento e CDI do exemplo que acompanha as taxas na fundação. */
export const EXAMPLE_NET_WORTH = 1_000_000;
const EXAMPLE_YIELD_POINTS = 15;
const EXAMPLE_CDI_POINTS = 10;

/** Fração do servidor ("0.0200") em pontos percentuais de régua (2). */
export const feeToPoints = (fraction: string) => Number(fraction) * 100;

/** Pontos percentuais da régua (1.5) no corpo da API: fração com quatro casas ("0.0150"). */
export const feeToBody = (points: number) => (points / 100).toFixed(4);

/** O passo da régua: décimos de ponto para tetos pequenos, ponto inteiro para os grandes. */
export const feeStep = (capPoints: number) => (capPoints <= 5 ? 0.1 : 1);

/** A régua arredondada ao passo, sem passar do teto. */
export function snapFee(points: number, capPoints: number) {
  const step = feeStep(capPoints);
  return Math.min(capPoints, Math.max(0, Math.round(points / step) * step));
}

/** Quanto a administração rende por mês: a taxa é ao ano e cobrada em 12 parcelas. */
export const managementPerMonth = (netWorth: number, points: number) => (netWorth * (points / 100)) / 12;

/** A performance do exemplo: o que passa do CDI, a parte do gestor e o que isso vale em pontos. */
export function performanceExample(points: number) {
  const extraPoints = EXAMPLE_YIELD_POINTS - EXAMPLE_CDI_POINTS;
  return { extraPoints, points: extraPoints * (points / 100) };
}

/** O quanto a cota está acima da marca d'água: a base sobre a qual a performance pode ser cobrada. */
export const aboveWaterMark = (nav: number, waterMark: number | null) =>
  waterMark === null ? 0 : Math.max(0, nav - waterMark);
