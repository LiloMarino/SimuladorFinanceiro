import { independenceGoal, WITHDRAWAL_RATE_RANGE } from "@/shared/lib/financial-independence";
import { normalizeNumberString } from "@/shared/lib/utils";

export const WITHDRAWAL_RATE_MESSAGE = `A taxa fica entre ${WITHDRAWAL_RATE_RANGE.min * 100}% e ${WITHDRAWAL_RATE_RANGE.max * 100}% ao ano`;

/** Campo de dinheiro com valor acima de zero. */
export const isPositiveMoney = (field: string) => Number(normalizeNumberString(field)) > 0;

/** Taxa de retirada como fração ao ano (0,04 = 4%) dentro da faixa que o servidor aceita. */
export const isWithdrawalRate = (rate: number) =>
  rate >= WITHDRAWAL_RATE_RANGE.min - 1e-9 && rate <= WITHDRAWAL_RATE_RANGE.max + 1e-9;

/** O campo da taxa guarda o percentual ao ano que o jogador digita ("4" é 4%); aqui vira fração. */
export const withdrawalRateFraction = (field: string) => Number(normalizeNumberString(field)) / 100;

/** A meta do viver de renda calculada dos campos; nula enquanto despesa ou taxa estão inválidas. */
export function calculatedGoal(monthlyExpense: string, withdrawalRate: string) {
  const rate = withdrawalRateFraction(withdrawalRate);
  return isPositiveMoney(monthlyExpense) && isWithdrawalRate(rate)
    ? independenceGoal(Number(normalizeNumberString(monthlyExpense)), rate)
    : null;
}

/** A taxa no corpo da API: fração ao ano com quatro casas ("4" → "0.0400"). */
export const withdrawalRateToBody = (field: string) => withdrawalRateFraction(field).toFixed(4);
