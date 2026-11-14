import { normalizeNumberString } from "@/shared/lib/utils";
import { moneyToBody } from "@/shared/lib/utils/money-field";
import type { FundContributionRequest, PortfolioState } from "@/types";

type Position = PortfolioState["variable_income"][number];

/** As ações marcadas para ir à gestora: ticker → quantidade digitada. */
export type StockPicks = Record<string, string>;

/** O que da posição está livre para integralizar (o que está em ordem aberta fica de fora). */
export const freeSize = (position: Position) => Math.max(0, Number(position.size) - Number(position.reserved));

/** O caixa digitado ("R$ 1.234,56") em reais. */
export const cashOf = (text: string) => Number(normalizeNumberString(text)) || 0;

/** A quantidade digitada de uma ação marcada: inteira, entre 1 e o que está livre; fora disso vale 0. */
export function pickedQuantity(text: string | undefined, position: Position) {
  const quantity = Number(text);
  return Number.isInteger(quantity) && quantity >= 1 && quantity <= freeSize(position) ? quantity : 0;
}

/** O valor de mercado das ações marcadas. */
export function picksValue(picks: StockPicks, positions: Position[]) {
  return positions.reduce(
    (sum, position) => sum + pickedQuantity(picks[position.ticker], position) * Number(position.current_price),
    0,
  );
}

/** Tudo certo para enviar: algo foi levado e cada ação marcada tem quantidade válida. */
export function contributionReady(cashText: string, picks: StockPicks, positions: Position[], availableCash: number) {
  const cash = cashOf(cashText);
  const picked = Object.keys(picks);
  const picksValid = positions
    .filter((position) => picked.includes(position.ticker))
    .every((position) => pickedQuantity(picks[position.ticker], position) > 0);
  return cash <= availableCash + 1e-9 && picksValid && (cash > 0 || picked.length > 0);
}

/** O corpo da integralização: o caixa e as ações marcadas. */
export function contributionBody(cashText: string, picks: StockPicks): FundContributionRequest {
  return {
    cash: cashOf(cashText) > 0 ? moneyToBody(cashText) : "0.00",
    stocks: Object.entries(picks).map(([ticker, quantity]) => ({ ticker, quantity: Number(quantity) })),
  };
}
