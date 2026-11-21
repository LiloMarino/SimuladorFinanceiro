import { keepPreviousData, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { FundIssuanceSubscriptionPreview } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";
import { fetchPreviewOutcome, outcomeOfPreviewEvent, type PreviewOutcome } from "@/shared/lib/realtime/preview-outcome";

/**
 * O custo e a parte do cotista depois de comprar `quotas` cotas na preferência da emissão. O servidor
 * guarda o último pedido e entrega a prévia nova por `fund_subscription_preview:{id}`.
 */
export function useFundSubscriptionPreview(fundId: number, quotas: number) {
  const queryClient = useQueryClient();
  const queryKey = fundKeys.subscriptionPreview(fundId, quotas);

  useRealtime(
    `fund_subscription_preview:${fundId}`,
    (event) => {
      if (event.quotas !== quotas) return;
      void applyRealtime<PreviewOutcome<FundIssuanceSubscriptionPreview>>(
        queryClient,
        queryKey,
        outcomeOfPreviewEvent(event),
      );
    },
    quotas > 0,
  );

  const { data, ...query } = useQuery({
    queryKey,
    queryFn: ({ signal }) =>
      fetchPreviewOutcome<FundIssuanceSubscriptionPreview>(
        `/api/funds/${fundId}/issuance/subscription-preview?quotas=${quotas}`,
        { signal },
      ),
    enabled: quotas > 0,
    placeholderData: keepPreviousData,
    staleTime: 0,
  });

  return { ...query, preview: data?.preview ?? undefined, refused: data?.refused ?? null };
}
