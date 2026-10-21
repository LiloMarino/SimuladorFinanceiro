import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { EconomicIndicators } from "@/types";

export function useEconomicIndicators() {
  return useQuery({
    queryKey: queryKeys.economicIndicators(),
    queryFn: ({ signal }) => apiFetch<EconomicIndicators>("/api/economic-indicators", { signal }),
  });
}
