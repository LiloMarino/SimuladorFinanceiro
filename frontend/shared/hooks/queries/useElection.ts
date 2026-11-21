import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { ElectionPanel } from "@/types";

/**
 * Datas, partidos, pesquisas, resultados e rankings da eleição da partida. Cada mudança do
 * governo traz o painel de quem olha por election_update; a cada montagem a consulta confere de novo.
 */
export function useElection({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.election(),
    queryFn: ({ signal }) => apiFetch<ElectionPanel>("/api/government/election", { signal }),
    enabled,
    staleTime: 0,
  });

  useRealtime(
    "election_update",
    (election) => {
      void applyRealtime<ElectionPanel>(queryClient, queryKeys.election(), election);
    },
    enabled,
  );

  return query;
}
