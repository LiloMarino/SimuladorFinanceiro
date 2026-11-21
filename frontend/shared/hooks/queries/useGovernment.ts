import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { GovernmentPanel } from "@/types";

/**
 * Impostos em vigor, aprovação, fila do Congresso e a carteira do presidente. Cada mudança do
 * governo traz o painel de quem olha por government_panel_update; a cada montagem a consulta confere de novo.
 */
export function useGovernment({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.government(),
    queryFn: ({ signal }) => apiFetch<GovernmentPanel>("/api/government", { signal }),
    enabled,
    staleTime: 0,
  });

  useRealtime(
    "government_panel_update",
    (panel) => {
      void applyRealtime<GovernmentPanel>(queryClient, queryKeys.government(), panel);
    },
    enabled,
  );

  return query;
}
