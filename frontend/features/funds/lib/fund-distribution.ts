/** O passo da régua da parte distribuída, em pontos percentuais. */
export const DISTRIBUTION_STEP = 5;

/** Fração do servidor ("0.9500") em pontos da régua (95). */
export const rateToPoints = (fraction: string) => Math.round(Number(fraction) * 100);

/** Pontos da régua (95) no corpo da API: fração com quatro casas ("0.9500"). */
export const rateToBody = (points: number) => (points / 100).toFixed(4);

/** Quanto uma parte distribuída paga de um lucro realizado; mês sem lucro não paga nada. */
export const distributedOf = (profit: number, points: number) => Math.max(0, profit) * (points / 100);
