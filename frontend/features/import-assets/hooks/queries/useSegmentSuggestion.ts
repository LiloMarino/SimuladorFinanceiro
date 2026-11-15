import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StockSuggestion } from "@/types";

/** Setor, segmento, ações em circulação e alavanca que o yFinance sugere para o código. */
export function useSegmentSuggestion(ticker: string) {
  return useQuery({
    queryKey: queryKeys.segmentSuggestion(ticker),
    queryFn: ({ signal }) =>
      apiFetch<StockSuggestion | null>(`/api/import-assets/stocks/${ticker}/suggestion`, { signal }),
    staleTime: Infinity,
  });
}
