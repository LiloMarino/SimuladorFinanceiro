import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { FixedIncomeOffer } from "@/types";

/** Títulos de renda fixa com a taxa do dia; quando a lista muda (fixed_assets_update), busca de novo. */
export function useFixedIncomeAssets() {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.fixedIncomeList(),
    queryFn: ({ signal }) => apiFetch<FixedIncomeOffer[]>("/api/fixed-income", { signal }),
  });

  useRealtime("fixed_assets_update", () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.fixedIncomeList() });
  });

  return query;
}
