import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { Trade } from "@/types";

/** Execuções da sala no ativo. */
export function useTrades(ticker: string, { enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: queryKeys.trades(ticker),
    queryFn: ({ signal }) => apiFetch<Trade[]>(`/api/variable-income/${ticker}/trades`, { signal }),
    enabled,
  });
}
