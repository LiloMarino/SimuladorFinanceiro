import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { StockDetails } from "@/types";

/** Detalhes de uma ação específica, mantida viva via stock_update:{ticker}. */
export function useVariableIncomeStock(ticker: string | undefined) {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.variableIncomeStock(ticker ?? ""),
    queryFn: ({ signal }) => apiFetch<StockDetails>(`/api/variable-income/${ticker}`, { signal }),
    enabled: !!ticker,
  });

  useRealtime(
    `stock_update:${ticker}`,
    ({ stock }) => {
      queryClient.setQueryData(queryKeys.variableIncomeStock(ticker ?? ""), (prev: StockDetails | undefined) => ({
        ...prev,
        ...stock,
        history: prev?.history ?? [],
      }));
    },
    !!ticker,
  );

  return query;
}
