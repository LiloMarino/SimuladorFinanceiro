import type { ProfessionMechanic } from "@/types";

export type RetireeMechanic = Extract<ProfessionMechanic, { kind: "retiree" }>;

const centsOf = (value: number) => Math.round(value * 100) / 100;

/** Quanto tempo o saldo está no plano, em texto: "3 anos e 4 meses", "1 ano", "5 meses". */
export function planTime(months: number) {
  const years = Math.floor(months / 12);
  const rest = months % 12;
  const yearsText = `${years} ${years === 1 ? "ano" : "anos"}`;
  const restText = `${rest} ${rest === 1 ? "mês" : "meses"}`;
  if (years === 0) return restText;
  return rest === 0 ? yearsText : `${yearsText} e ${restText}`;
}

/** A renda por mês que `amount` convertido paga com a fração de renda do juro real de hoje. */
export function convertedIncome(amount: number, incomeRate: string) {
  return centsOf(amount * Number(incomeRate));
}

/** O que o resgate de `amount` deixa com a Receita e o que cai no caixa, com a alíquota dada. */
export function redeemSplit(amount: number, rate: string) {
  const tax = centsOf(amount * Number(rate));
  return { tax, net: centsOf(amount - tax) };
}

/** A faixa seguinte do IR: em quantos meses chega e quanto a mais cai no caixa esperando por ela; nulo na última faixa. */
export function nextBracketGain(mechanic: RetireeMechanic, amount: number) {
  const { next_rate, next_rate_months, next_rate_on } = mechanic;
  if (next_rate === null || next_rate_months === null || next_rate_on === null) return null;
  const now = redeemSplit(amount, mechanic.redeem_rate).net;
  const later = redeemSplit(amount, next_rate).net;
  return { months: next_rate_months, rate: next_rate, on: next_rate_on, laterNet: later, gain: centsOf(later - now) };
}

/** Meses em texto: "1 mês", "8 meses". */
export const monthsText = (months: number) => `${months} ${months === 1 ? "mês" : "meses"}`;
