import type { AssetClass } from "@/types";
import { parseLocalDate } from "@/shared/lib/utils/display";

/** Alíquota do IR sobre o lucro de cada classe, a mesma da apuração do backend. */
export const INCOME_TAX_RATE: Record<AssetClass, number> = {
  STOCK: 0.15,
  FII: 0.2,
  ETF: 0.15,
  BDR: 0.15,
};

/** Mês das vendas que geram o DARF: a cobrança sai no último dia útil do mês seguinte. */
export function salesMonthName(dueDate: string): string {
  const due = parseLocalDate(dueDate);
  return new Intl.DateTimeFormat("pt-BR", { month: "long" }).format(new Date(due.getFullYear(), due.getMonth() - 1, 1));
}
