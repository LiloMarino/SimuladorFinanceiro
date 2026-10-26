import type { StockDetails } from "@/types";

/** Não cria um detalhe incompleto antes do REST nem deixa um evento atrasado regredir a cotação. */
export function mergeStockUpdate(
  previous: StockDetails | undefined,
  candle: Omit<StockDetails, "history">,
): StockDetails | undefined {
  if (!previous || candle.price_date < previous.price_date) return previous;
  const history = [...previous.history];
  const index = history.findIndex((row) => row.price_date >= candle.price_date);
  if (index < 0) history.push(candle);
  else if (history[index]?.price_date === candle.price_date) history[index] = candle;
  else history.splice(index, 0, candle);
  return { ...previous, ...candle, history };
}
