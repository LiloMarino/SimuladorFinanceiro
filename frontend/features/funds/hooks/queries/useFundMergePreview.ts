import { keepPreviousData, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { FundMergePreview } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";
import { fetchPreviewOutcome, outcomeOfPreviewEvent, type PreviewOutcome } from "@/shared/lib/realtime/preview-outcome";

/**
 * O que a fusão faz hoje: `fundId` incorpora `daughterFundId`, com a troca de cotas e o patrimônio depois.
 * O servidor guarda o último pedido e entrega a prévia nova por `fund_merge_preview:{id}`.
 */
export function useFundMergePreview(fundId: number, daughterFundId: number) {
  const queryClient = useQueryClient();
  const queryKey = fundKeys.mergePreview(fundId, daughterFundId);

  useRealtime(`fund_merge_preview:${fundId}`, (event) => {
    if (event.daughter_fund_id !== daughterFundId) return;
    void applyRealtime<PreviewOutcome<FundMergePreview>>(queryClient, queryKey, outcomeOfPreviewEvent(event));
  });

  const { data, ...query } = useQuery({
    queryKey,
    queryFn: ({ signal }) =>
      fetchPreviewOutcome<FundMergePreview>(
        `/api/funds/${fundId}/assembly/merge/preview?daughter_fund_id=${daughterFundId}`,
        { signal },
      ),
    placeholderData: keepPreviousData,
    staleTime: 0,
  });

  return { ...query, preview: data?.preview ?? undefined, refused: data?.refused ?? null };
}
