import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { TreasuryCatalog } from "@/types";
import { isCatalogStale } from "../../lib/treasury";

/** Os títulos à venda e o termômetro do risco; o catálogo renova no primeiro dia simulado que passa da revisão ou de um vencimento. */
export function useTreasuryCatalog() {
  const queryClient = useQueryClient();

  useRealtime("simulation_update", ({ current_date }) => {
    const catalog = queryClient.getQueryData<TreasuryCatalog>(queryKeys.treasuryCatalog());
    if (catalog && isCatalogStale(catalog, current_date)) {
      void queryClient.invalidateQueries({ queryKey: queryKeys.treasuryCatalog() });
    }
  });

  return useQuery({
    queryKey: queryKeys.treasuryCatalog(),
    queryFn: ({ signal }) => apiFetch<TreasuryCatalog>("/api/treasury", { signal }),
  });
}
