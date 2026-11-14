import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundIssuanceSubscriptionRequest } from "@/types";
import { fundKeys } from "../fund-keys";

/** Compra cotas novas na preferência da emissão, ao preço fixo do anúncio. */
export function useSubscribeFundIssuance(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: FundIssuanceSubscriptionRequest) =>
      apiFetch<void>(`/api/funds/${fundId}/issuance/subscriptions`, { method: "POST", body: request }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
