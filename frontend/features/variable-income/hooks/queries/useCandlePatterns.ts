import { keepPreviousData, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtimeDelta } from "@/shared/lib/realtime/apply-realtime";
import type { CandlePatterns } from "@/types";
import { mergePatternsUpdate } from "../../lib/asset-feed";

/** Padrões de vela do histórico até a data da simulação; a cada pregão o aviso traz os que mudaram. */
export function useCandlePatterns(ticker: string, { enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();
  const queryKey = queryKeys.candlePatterns(ticker);

  useRealtime(
    `candle_patterns_update:${ticker}`,
    (update) => {
      void applyRealtimeDelta<CandlePatterns>(queryClient, queryKey, (current) => mergePatternsUpdate(current, update));
    },
    enabled,
  );

  return useQuery({
    queryKey,
    queryFn: ({ signal }) => apiFetch<CandlePatterns>(`/api/variable-income/${ticker}/patterns`, { signal }),
    enabled,
    placeholderData: keepPreviousData,
  });
}
