import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { GovernmentStatus } from "@/types";

/**
 * O resumo do governo que as telas de qualquer página leem: quem governa, a aprovação geral, a fila do
 * Congresso em número e o congelamento do presidente. Cada mudança do governo traz o resumo de quem olha
 * por government_status_update; a cada montagem a consulta confere de novo.
 */
export function useGovernmentStatus({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.governmentStatus(),
    queryFn: ({ signal }) => apiFetch<GovernmentStatus>("/api/government/status", { signal }),
    enabled,
    staleTime: 0,
  });

  useRealtime(
    "government_status_update",
    (status) => {
      void applyRealtime<GovernmentStatus>(queryClient, queryKeys.governmentStatus(), status);
    },
    enabled,
  );

  return query;
}
