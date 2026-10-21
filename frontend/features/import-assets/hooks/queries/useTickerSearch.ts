import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { TickerSuggestion } from "@/types";

/** Códigos da B3 que batem com o texto digitado. */
export function useTickerSearch(query: string, { enabled }: { enabled: boolean }) {
  return useQuery({
    queryKey: queryKeys.tickerSearch(query.toUpperCase()),
    queryFn: ({ signal }) =>
      apiFetch<TickerSuggestion[]>(`/api/import-assets/tickers?q=${encodeURIComponent(query)}`, { signal }),
    enabled,
    staleTime: Infinity,
    retry: false,
  });
}
