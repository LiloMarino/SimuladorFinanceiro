import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { PerformanceReport } from "@/types";

/** Ranking e histórico de patrimônio dos jogadores; o ranking é do backend, então cada snapshot novo refaz a busca. */
export function useStatistics() {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.statistics(),
    queryFn: ({ signal }) => apiFetch<PerformanceReport>("/api/statistics", { signal }),
  });

  useRealtime("statistics_snapshot_update", () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.statistics() });
  });

  return query;
}
