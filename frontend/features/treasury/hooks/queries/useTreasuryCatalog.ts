import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { TreasuryCatalog } from "@/types";

/** Os títulos à venda e o termômetro do risco; o servidor entrega o catálogo novo por `treasury_catalog_update` quando a revisão ou um vencimento o renova. */
export function useTreasuryCatalog() {
  const queryClient = useQueryClient();

  useRealtime("treasury_catalog_update", (catalog) => {
    void applyRealtime<TreasuryCatalog>(queryClient, queryKeys.treasuryCatalog(), catalog);
  });

  return useQuery({
    queryKey: queryKeys.treasuryCatalog(),
    queryFn: ({ signal }) => apiFetch<TreasuryCatalog>("/api/treasury", { signal }),
    staleTime: 0,
  });
}
