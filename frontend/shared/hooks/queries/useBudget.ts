import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { Budget } from "@/types";

/**
 * A conta do governo: cada dia do pregão e cada ação do governo trazem o orçamento por
 * budget_update. O cache vale enquanto a tela escuta o evento; a cada montagem a consulta confere de novo.
 */
export function useBudget({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.budget(),
    queryFn: ({ signal }) => apiFetch<Budget>("/api/government/budget", { signal }),
    enabled,
    staleTime: 0,
  });

  useRealtime(
    "budget_update",
    (budget) => {
      void applyRealtime<Budget>(queryClient, queryKeys.budget(), budget);
    },
    enabled,
  );

  return query;
}
