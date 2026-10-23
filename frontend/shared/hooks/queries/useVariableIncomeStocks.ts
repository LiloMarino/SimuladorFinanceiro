import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { MarketQuote } from "@/types";

/**
 * Lista de mercado, mantida viva via stocks_update. O evento traz só a cotação do
 * dia: o mini gráfico e o setor vêm da busca, e o último ponto do gráfico segue o
 * fechamento ao vivo (num pregão novo, o ponto mais antigo sai).
 */
export function useVariableIncomeStocks() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.variableIncomeList(),
    queryFn: ({ signal }) => apiFetch<MarketQuote[]>("/api/variable-income", { signal }),
  });

  useRealtime("stocks_update", ({ stocks }) => {
    queryClient.setQueryData(queryKeys.variableIncomeList(), (prev: MarketQuote[] | undefined) => {
      if (!prev) return prev;
      const byTicker = new Map(stocks.map((s) => [s.ticker, s]));
      return prev.map((quote) => {
        const candle = byTicker.get(quote.ticker);
        if (!candle) return quote;
        const newDay = candle.price_date !== quote.price_date;
        const sparkline = newDay
          ? [...quote.sparkline.slice(1), candle.close]
          : [...quote.sparkline.slice(0, -1), candle.close];
        return { ...quote, ...candle, sparkline };
      });
    });
  });

  return query;
}
