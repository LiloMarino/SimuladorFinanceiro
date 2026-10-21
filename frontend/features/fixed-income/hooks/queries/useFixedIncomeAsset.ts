import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FixedIncomeOffer } from "@/types";

/** Um título de renda fixa, com a taxa do dia. */
export function useFixedIncomeAsset(id: string | undefined) {
  return useQuery({
    queryKey: queryKeys.fixedIncomeAsset(id ?? ""),
    queryFn: ({ signal }) => apiFetch<FixedIncomeOffer>(`/api/fixed-income/${id}`, { signal }),
    enabled: !!id,
  });
}
