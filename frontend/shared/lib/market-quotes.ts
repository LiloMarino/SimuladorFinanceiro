import type { MarketQuote, SimulationEvents } from "@/types";

type Candle = SimulationEvents["stocks_update"]["stocks"][number];

/**
 * Aplica as velas do dia à lista de mercado: o último ponto do mini gráfico segue o
 * fechamento ao vivo e, num pregão novo, o ponto mais antigo sai. `hasUnknown` marca vela
 * de um ticker que a lista ainda não tem: o ativo acabou de ser listado e a lista
 * precisa ser buscada de novo, porque o evento não traz setor nem mini gráfico.
 */
export function applyStocksUpdate(quotes: MarketQuote[], candles: Candle[]) {
  const byTicker = new Map(candles.map((candle) => [candle.ticker, candle]));
  const known = new Set(quotes.map((quote) => quote.ticker));

  const merged = quotes.map((quote) => {
    const candle = byTicker.get(quote.ticker);
    if (!candle) return quote;
    const newDay = candle.price_date !== quote.price_date;
    const sparkline = newDay
      ? [...quote.sparkline.slice(1), candle.close]
      : [...quote.sparkline.slice(0, -1), candle.close];
    return { ...quote, ...candle, sparkline };
  });

  return { quotes: merged, hasUnknown: candles.some((candle) => !known.has(candle.ticker)) };
}
