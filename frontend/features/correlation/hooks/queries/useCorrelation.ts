import { keepPreviousData } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { CorrelationMatrix, CorrelationWindow } from "@/types";

/** Matriz dos tickers escolhidos; sem `end`, o backend usa a data da simulação ou o último pregão. */
export function useCorrelation(tickers: string[], window: CorrelationWindow, end: string | null) {
  const params = new URLSearchParams([...tickers.map((t) => ["tickers", t]), ["window", window]]);
  if (end) params.set("end", end);

  return useApiQuery({
    queryKey: queryKeys.correlation(tickers, window, end),
    queryFn: ({ signal }) => apiFetch<CorrelationMatrix>(`/api/correlation?${params}`, { signal }),
    enabled: tickers.length > 0,
    placeholderData: keepPreviousData,
  });
}
