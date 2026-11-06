import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { TreasuryCatalog } from "@/types";

/** Os títulos à venda e o termômetro do risco; a taxa é revista no dia 1º, então o catálogo renova nele. */
export function useTreasuryCatalog() {
  const queryClient = useQueryClient();

  useRealtime("simulation_update", ({ current_date }) => {
    if (current_date.endsWith("-01")) {
      void queryClient.invalidateQueries({ queryKey: queryKeys.treasuryCatalog() });
    }
  });

  return useQuery({
    queryKey: queryKeys.treasuryCatalog(),
    queryFn: ({ signal }) => apiFetch<TreasuryCatalog>("/api/treasury", { signal }),
  });
}
