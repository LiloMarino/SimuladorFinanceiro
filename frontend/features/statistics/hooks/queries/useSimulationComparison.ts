import { keepPreviousData } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { PerformanceReport } from "@/types";

/** Ranking e histórico de cada jogador em cada simulação salva selecionada. */
export function useSimulationComparison(simulationIds: number[]) {
  const params = new URLSearchParams(simulationIds.map((id) => ["simulation_ids", String(id)]));

  return useApiQuery({
    queryKey: queryKeys.statisticsComparison(simulationIds),
    queryFn: ({ signal }) => apiFetch<PerformanceReport>(`/api/statistics/compare?${params}`, { signal }),
    enabled: simulationIds.length > 0,
    placeholderData: keepPreviousData,
  });
}
