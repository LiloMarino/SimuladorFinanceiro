import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { FixedIncomeAssetApi } from "@/types";

/** Hall de ativos de renda fixa disponíveis, mantido vivo via fixed_assets_update. */
export function useFixedIncomeAssets() {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.fixedIncomeList(),
    queryFn: ({ signal }) => apiFetch<FixedIncomeAssetApi[]>("/api/fixed-income", { signal }),
  });

  useRealtime("fixed_assets_update", ({ assets }) => {
    queryClient.setQueryData(queryKeys.fixedIncomeList(), assets);
  });

  return query;
}
