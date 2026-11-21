import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { PromisesPanel } from "@/types";

/** As promessas da chapa de quem fundou o partido: a lista anunciada, as medidas que se prometem e o prazo; cada mudança do governo as traz por promises_update. */
export function usePromises(enabled: boolean) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.promises(),
    queryFn: ({ signal }) => apiFetch<PromisesPanel>("/api/government/promises", { signal }),
    enabled,
    staleTime: 0,
  });

  useRealtime(
    "promises_update",
    (promises) => {
      void applyRealtime<PromisesPanel>(queryClient, queryKeys.promises(), promises);
    },
    enabled,
  );

  return query;
}
