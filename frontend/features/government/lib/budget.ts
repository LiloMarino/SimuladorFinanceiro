import { endOfMonth, format } from "date-fns";
import { displayPoints, displayPremiumPoints } from "@/shared/lib/budget-metrics";
import { displayMoneyLarge, displayPercent, parseLocalDate } from "@/shared/lib/utils/display";
import type { Budget, BudgetEffect, BudgetMonth, BudgetTax } from "@/types";
import type { ApprovalFactor, GroupApproval } from "./approval";
import { percentLabel } from "./government";

const MINUS = "−";

export type BudgetUnit = "month" | "year";

/** Fração do PIB com duas casas ("0,09%"); abaixo de 0,01% ganha a terceira ("0,003%"). */
export function shareLabel(fraction: string | number) {
  const value = Number(fraction);
  return displayPercent(value, value !== 0 && Math.abs(value) < 0.0001 ? 3 : 2).replace("-", MINUS);
}

/** O mesmo com sinal explícito ("+0,003%", "−0,02%"); zero vira traço. */
export function signedShareLabel(fraction: string | number) {
  const value = Number(fraction);
  if (value === 0) return "—";
  return `${value > 0 ? "+" : ""}${shareLabel(value)}`;
}

/** A receita, o gasto ou o resultado no mês ou por ano: em reais no mês, em % do PIB no ano. */
export function amountLabel(unit: BudgetUnit, fraction: string | number, amount: string | number) {
  return unit === "month" ? displayMoneyLarge(amount) : shareLabel(fraction);
}

export type AccountBars = {
  /** Larguras em fração da barra mais longa */
  in: { revenue: number; deficit: number };
  out: { spending: number; interest: number; surplus: number };
};

/** As duas barras da conta: o que entra (receita mais o déficit) e o que sai (gasto, juros e a sobra) fecham no mesmo comprimento. */
export function accountBars(month: Pick<BudgetMonth, "revenue" | "spending" | "interest" | "result">): AccountBars {
  const revenue = Number(month.revenue);
  const spending = Number(month.spending);
  const interest = Number(month.interest);
  const result = Number(month.result);
  const deficit = Math.max(0, -result);
  const surplus = Math.max(0, result);
  const longest = Math.max(revenue + deficit, spending + interest + surplus) || 1;
  return {
    in: { revenue: revenue / longest, deficit: deficit / longest },
    out: { spending: spending / longest, interest: interest / longest, surplus: surplus / longest },
  };
}

/** Resultado negativo pesa em vermelho, positivo em verde. */
export function resultTone(result: string | number): "destructive" | "success" | "default" {
  const value = Number(result);
  if (value < 0) return "destructive";
  return value > 0 ? "success" : "default";
}

/** O último dia do mês de `today`, quando o primeiro fechamento sai. */
export function closingDay(today: string) {
  return format(endOfMonth(parseLocalDate(today)), "yyyy-MM-dd");
}

/** A dívida contra a de 12 fechamentos atrás ("▼ 0,9 ponto em 12 meses"); nulo até a partida ter um ano de contas. */
export function debtChangeNote(history: BudgetMonth[], month: BudgetMonth) {
  const closed = history.filter((m) => m.closed);
  const year = closed.at(-13);
  if (!year) return null;
  const change = (Number(month.debt) - Number(year.debt)) * 100;
  const points = Math.abs(change);
  if (Math.round(points * 10) === 0) return "estável em 12 meses";
  return `${change > 0 ? "▲" : "▼"} ${displayPoints(points, 1)} em 12 meses`;
}

/** Com a dívida acima do piso, o prêmio em pontos; abaixo, quanto falta para ele começar. */
export function premiumNote(month: Pick<BudgetMonth, "debt" | "premium">, floor: string) {
  if (Number(month.premium) > 0) return `prêmio de ${displayPremiumPoints(month.premium)}`;
  const left = (Number(floor) - Number(month.debt)) * 100;
  return `sem prêmio · faltam ${displayPoints(left, 1)} para o prêmio`;
}

/** Dívida acima do piso pede atenção; acima de 100% do PIB, alerta. */
export function debtTone(month: Pick<BudgetMonth, "debt" | "premium">): "destructive" | "warning" | "default" {
  if (Number(month.debt) > 1) return "destructive";
  return Number(month.premium) > 0 ? "warning" : "default";
}

/** Alíquota do imposto na tabela: "15%", "isenta" ou, na renda fixa, a faixa "22,5% → 15%". */
function taxRateLabel(rate: string | null, top: string | null, floor: string | null) {
  if (top !== null && floor !== null && top !== floor) return `${percentLabel(top)} → ${percentLabel(floor)}`;
  if (rate === null || Number(rate) === 0) return "isenta";
  return percentLabel(rate);
}

/** A alíquota de hoje do imposto. */
export function todayRateLabel(tax: BudgetTax) {
  return taxRateLabel(tax.rate, tax.top_rate, tax.floor_rate);
}

/** A alíquota da política padrão, na mesma escrita da de hoje. */
export function defaultRateLabel(tax: BudgetTax) {
  return taxRateLabel(tax.default_rate, tax.default_top_rate, tax.default_floor_rate);
}

/** Receita de um imposto; sem arrecadação, traço. */
export function taxRevenueLabel(tax: Pick<BudgetTax, "revenue">) {
  return Number(tax.revenue) === 0 ? "—" : shareLabel(tax.revenue);
}

export type DebtRow = { time: number; history?: number; projection?: number };

/** A dívida em fração do PIB mês a mês: os fechamentos já feitos e, a partir do último, a projeção se nada mais mudar. */
export function debtSeries(budget: Pick<Budget, "month" | "history" | "projection">): DebtRow[] {
  const closed = budget.history.filter((m) => m.closed);
  const rows: DebtRow[] = closed.map((m) => ({ time: parseLocalDate(m.month_end).getTime(), history: Number(m.debt) }));
  const start = closed.at(-1) ?? budget.month;
  const projected: DebtRow[] = budget.projection.map((m) => ({
    time: parseLocalDate(m.month_end).getTime(),
    projection: Number(m.debt),
  }));
  // A projeção parte do último ponto conhecido para a linha tracejada encostar na cheia
  const anchor: DebtRow = { time: parseLocalDate(start.month_end).getTime(), projection: Number(start.debt) };
  if (rows.length > 0) rows[rows.length - 1] = { ...rows[rows.length - 1], ...anchor };
  else rows.push(anchor);
  return [...rows, ...projected];
}

/** Os fatores do grupo que vêm da conta do país: o desemprego e o prêmio de risco. */
export function budgetFactors(group: { factors: GroupApproval["factors"] }) {
  return group.factors.filter(
    (factor): factor is ApprovalFactor & { kind: "UNEMPLOYMENT" | "RISK_PREMIUM" } =>
      factor.kind === "UNEMPLOYMENT" || factor.kind === "RISK_PREMIUM",
  );
}

/** Abaixo disso a medida mal pesa na receita do país e o número vira "≈ 0,00%". */
const NEGLIGIBLE_AMOUNT = 50_000_000;

export type EffectHeadline = { value: string; detail: string; tone: "success" | "destructive" | "default" };

/** O destaque da estimativa: quanto a medida muda a receita, em % do PIB por ano e em reais por ano. */
export function effectHeadline(effect: Pick<BudgetEffect, "revenue_change" | "revenue_change_amount">): EffectHeadline {
  const amount = Math.abs(Number(effect.revenue_change_amount));
  if (amount < NEGLIGIBLE_AMOUNT) {
    return { value: "≈ 0,00%", detail: "menos de R$ 50 mi por ano", tone: "default" };
  }
  return {
    value: signedShareLabel(effect.revenue_change),
    detail: `do PIB por ano · cerca de ${displayMoneyLarge(amount)} por ano`,
    tone: Number(effect.revenue_change) > 0 ? "success" : "destructive",
  };
}

/** A variação relativa entre dois valores ("−18%"); nula quando o de antes é zero ou nada mudou. */
export function relativeChange(before: string, after: string) {
  const from = Number(before);
  if (from === 0) return null;
  const change = Math.round(((Number(after) - from) / from) * 100);
  if (change === 0) return null;
  return `${change > 0 ? "+" : MINUS}${Math.abs(change)}%`;
}

/** O prazo da alíquota sai em % de uma casa quando existe; isento não tem alíquota. */
export function rateChangeLabel(before: string | null, after: string | null) {
  const side = (rate: string | null) => (rate === null ? "isenta" : percentLabel(rate));
  return `${side(before)} → ${side(after)}`;
}
