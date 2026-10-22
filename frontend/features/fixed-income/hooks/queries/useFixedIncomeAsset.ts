import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FixedIncomeOffer } from "@/types";
import { useRealtime } from "@/shared/hooks/useRealtime";

/** Um título de renda fixa, com a taxa do dia. */
export function useFixedIncomeAsset(id: string | undefined) {
  const client = useQueryClient();
  useRealtime("simulation_update", () => {
    if (id) void client.invalidateQueries({ queryKey: queryKeys.fixedIncomeAsset(id) });
  });
  return useQuery({
    queryKey: queryKeys.fixedIncomeAsset(id ?? ""),
    queryFn: ({ signal }) => apiFetch<FixedIncomeOffer>(`/api/fixed-income/${id}`, { signal }),
    enabled: !!id,
    staleTime: 0,
  });
}
