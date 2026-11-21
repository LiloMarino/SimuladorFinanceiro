import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { applyRealtimeDelta } from "@/shared/lib/realtime/apply-realtime";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { StockDetails } from "@/types";
import { mergeStockUpdate } from "../../lib/stock-history";

/** Detalhes de uma ação específica, mantida viva via stock_update:{ticker}. */
export function useVariableIncomeStock(ticker: string | undefined) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.variableIncomeStock(ticker ?? ""),
    queryFn: ({ signal }) => apiFetch<StockDetails>(`/api/variable-income/${ticker}`, { signal }),
    enabled: !!ticker,
  });

  useRealtime(
    `stock_update:${ticker}`,
    ({ stock }) => {
      void applyRealtimeDelta<StockDetails>(
        queryClient,
        queryKeys.variableIncomeStock(ticker ?? ""),
        (current) => mergeStockUpdate(current, stock) ?? null,
      );
    },
    !!ticker,
  );

  return query;
}
