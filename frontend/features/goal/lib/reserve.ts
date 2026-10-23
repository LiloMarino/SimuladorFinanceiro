// A régua da reserva vai de 0 a 6 meses; a partir daí é "6+"
export const RESERVE_FULL_MONTHS = 6;
export const RESERVE_FRAGILE_MONTHS = 3;

type ReserveTone = "success" | "warning" | "destructive";

/** Tom da reserva: crítico abaixo de 3 meses, de atenção até 6 e bom a partir de 6. */
export function reserveTone(months: number): ReserveTone {
  if (months >= RESERVE_FULL_MONTHS) return "success";
  if (months >= RESERVE_FRAGILE_MONTHS) return "warning";
  return "destructive";
}

/**
 * Os dois trechos da barra da reserva, em fração da régua de 0 a 6 meses: o caixa primeiro e a liquidez
 * diária logo depois. Os dois somam no máximo 1, então a barra cheia é "6+".
 */
export function reserveShares(cashMonths: number, dailyLiquidityMonths: number) {
  const cash = Math.min(Math.max(cashMonths, 0) / RESERVE_FULL_MONTHS, 1);
  const dailyLiquidity = Math.min(Math.max(dailyLiquidityMonths, 0) / RESERVE_FULL_MONTHS, 1 - cash);
  return { cash, dailyLiquidity };
}
