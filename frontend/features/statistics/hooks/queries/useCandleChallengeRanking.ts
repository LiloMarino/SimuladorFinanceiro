import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { CandleChallengeRanking } from "@/types";

/** Placar do desafio da vela da partida: acertos e respondidas de cada jogador. */
export function useCandleChallengeRanking(simulationIds: number[], { enabled = true }: { enabled?: boolean } = {}) {
  const params = new URLSearchParams(simulationIds.map((id) => ["simulation_ids", String(id)]));

  return useQuery({
    queryKey: queryKeys.candleChallengeRanking(simulationIds),
    queryFn: ({ signal }) => apiFetch<CandleChallengeRanking>(`/api/statistics/candle-challenge?${params}`, { signal }),
    enabled: enabled && simulationIds.length > 0,
  });
}
