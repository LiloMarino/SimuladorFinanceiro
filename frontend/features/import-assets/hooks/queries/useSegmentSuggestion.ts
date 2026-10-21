import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StockSegment } from "@/types";

/** Setor e segmento que o yFinance sugere para o código. */
export function useSegmentSuggestion(ticker: string) {
  return useQuery({
    queryKey: queryKeys.segmentSuggestion(ticker),
    queryFn: ({ signal }) =>
      apiFetch<StockSegment | null>(`/api/import-assets/stocks/${ticker}/suggestion`, { signal }),
    staleTime: Infinity,
  });
}
