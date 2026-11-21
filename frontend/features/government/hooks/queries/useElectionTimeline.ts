import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { ElectionTimeline } from "@/types";

/**
 * A linha do tempo do mapa: os anos de eleição, os pontos da régua e os marcos do ano escolhido.
 * O aviso traz a do ano em curso, que vale para a leitura sem ano e para a do próprio ano.
 */
export function useElectionTimeline(year: number | null) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.electionTimeline(year),
    queryFn: ({ signal }) =>
      apiFetch<ElectionTimeline>(`/api/government/map/timeline${year === null ? "" : `?year=${year}`}`, { signal }),
    staleTime: 0,
  });

  useRealtime("map_timeline_update", (timeline) => {
    void applyRealtime<ElectionTimeline>(queryClient, queryKeys.electionTimeline(null), timeline);
    void applyRealtime<ElectionTimeline>(queryClient, queryKeys.electionTimeline(timeline.year), timeline);
  });

  return query;
}
