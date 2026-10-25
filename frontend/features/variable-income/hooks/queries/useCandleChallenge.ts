import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { CandleChallenge } from "@/types";

/** A pergunta de hoje, a última resposta do jogador nesse ativo e o placar dele. */
export function useCandleChallenge(ticker: string, { enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  useRealtime(`stock_update:${ticker}`, () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.candleChallenge(ticker) });
  });

  return useQuery({
    queryKey: queryKeys.candleChallenge(ticker),
    queryFn: ({ signal }) => apiFetch<CandleChallenge>(`/api/variable-income/${ticker}/challenge`, { signal }),
    enabled,
  });
}
