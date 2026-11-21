import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { FixedIncomeOffer } from "@/types";
import { useRealtime } from "@/shared/hooks/useRealtime";

/** Um título de renda fixa, com a taxa do dia: o servidor entrega a oferta nova por `fixed_income_offer_update:{id}`. */
export function useFixedIncomeAsset(id: string | undefined) {
  const client = useQueryClient();
  useRealtime(
    `fixed_income_offer_update:${id ?? ""}`,
    (offer) => {
      if (id) void applyRealtime<FixedIncomeOffer>(client, queryKeys.fixedIncomeAsset(id), offer);
    },
    !!id,
  );
  return useQuery({
    queryKey: queryKeys.fixedIncomeAsset(id ?? ""),
    queryFn: ({ signal }) => apiFetch<FixedIncomeOffer>(`/api/fixed-income/${id}`, { signal }),
    enabled: !!id,
    staleTime: 0,
  });
}
