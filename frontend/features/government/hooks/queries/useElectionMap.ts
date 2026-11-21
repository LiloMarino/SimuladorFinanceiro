import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { ElectionMap } from "@/types";

/** O mapa do Brasil: pesquisa, resultado, rejeição e aprovação em cada estado e região; cada mudança do governo o traz por map_update. */
export function useElectionMap() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.electionMap(),
    queryFn: ({ signal }) => apiFetch<ElectionMap>("/api/government/map", { signal }),
    staleTime: 0,
  });

  useRealtime("map_update", (map) => {
    void applyRealtime<ElectionMap>(queryClient, queryKeys.electionMap(), map);
  });

  return query;
}
