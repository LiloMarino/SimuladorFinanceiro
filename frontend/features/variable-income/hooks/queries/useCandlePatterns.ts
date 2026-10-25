import { keepPreviousData, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { CandlePatterns } from "@/types";

/** Padrões de vela do histórico até a data da simulação, refeitos a cada pregão. */
export function useCandlePatterns(ticker: string, { enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  useRealtime(`stock_update:${ticker}`, () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.candlePatterns(ticker) });
  });

  return useQuery({
    queryKey: queryKeys.candlePatterns(ticker),
    queryFn: ({ signal }) => apiFetch<CandlePatterns>(`/api/variable-income/${ticker}/patterns`, { signal }),
    enabled,
    placeholderData: keepPreviousData,
  });
}
