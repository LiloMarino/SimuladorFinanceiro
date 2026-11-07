import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { AssetCorporateEvents } from "@/types";

/** Histórico de proventos, desdobramentos e grupamentos de um ativo, até o dia de hoje do jogo. */
export function useCorporateEvents(ticker: string | undefined) {
  return useQuery({
    queryKey: queryKeys.corporateEvents(ticker ?? ""),
    queryFn: ({ signal }) =>
      apiFetch<AssetCorporateEvents>(`/api/variable-income/${ticker}/corporate-events`, { signal }),
    enabled: !!ticker,
  });
}
