import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { FundMergePreview } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** O que a fusão faz hoje: `fundId` incorpora `daughterFundId`, com a troca de cotas e o patrimônio depois. */
export function useFundMergePreview(fundId: number, daughterFundId: number) {
  return useQuery({
    queryKey: fundKeys.mergePreview(fundId, daughterFundId),
    queryFn: ({ signal }) =>
      apiFetch<FundMergePreview>(`/api/funds/${fundId}/assembly/merge/preview?daughter_fund_id=${daughterFundId}`, {
        signal,
      }),
    placeholderData: keepPreviousData,
  });
}
