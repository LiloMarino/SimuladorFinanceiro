import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { PromiseBalance } from "@/types";

/** Os balanços das promessas dos governos que acabaram, do mais recente ao mais antigo; cada mudança do governo os traz por balances_update. */
export function useBalances(enabled: boolean) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.balances(),
    queryFn: ({ signal }) => apiFetch<PromiseBalance[]>("/api/government/balances", { signal }),
    enabled,
    staleTime: 0,
  });

  useRealtime(
    "balances_update",
    (balances) => {
      void applyRealtime<PromiseBalance[]>(queryClient, queryKeys.balances(), balances);
    },
    enabled,
  );

  return query;
}
