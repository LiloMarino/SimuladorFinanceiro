import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { FundIssuanceSubscriptionPreview } from "@/types";
import { fundKeys } from "../fund-keys";

/** O custo e a parte do cotista depois de comprar `quotas` cotas na preferência da emissão. */
export function useFundSubscriptionPreview(fundId: number, quotas: number) {
  return useQuery({
    queryKey: fundKeys.subscriptionPreview(fundId, quotas),
    queryFn: ({ signal }) =>
      apiFetch<FundIssuanceSubscriptionPreview>(`/api/funds/${fundId}/issuance/subscription-preview?quotas=${quotas}`, {
        signal,
      }),
    enabled: quotas > 0,
    placeholderData: keepPreviousData,
  });
}
