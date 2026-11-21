import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { AssetCorporateEvents } from "@/types";

/**
 * Histórico de proventos, desdobramentos e grupamentos de um ativo, até o dia de hoje do jogo.
 * Um provento ou desdobramento novo chega por `corporate_events_update:{ticker}`.
 */
export function useCorporateEvents(ticker: string | undefined) {
  const queryClient = useQueryClient();

  useRealtime(
    `corporate_events_update:${ticker ?? ""}`,
    (events) => {
      void applyRealtime<AssetCorporateEvents>(queryClient, queryKeys.corporateEvents(ticker ?? ""), events);
    },
    !!ticker,
  );

  return useQuery({
    queryKey: queryKeys.corporateEvents(ticker ?? ""),
    queryFn: ({ signal }) =>
      apiFetch<AssetCorporateEvents>(`/api/variable-income/${ticker}/corporate-events`, { signal }),
    staleTime: 0,
    enabled: !!ticker,
  });
}
