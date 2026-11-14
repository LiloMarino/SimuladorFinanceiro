import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundOfferRequest, FundSummary } from "@/types";
import { fundKeys } from "../fund-keys";

/** Abre a oferta pública: a cota entra no mercado ao patrimônio por cota do dia. */
export function useOpenFundOffer(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: FundOfferRequest) =>
      apiFetch<FundSummary>(`/api/funds/${fundId}/offer`, { method: "POST", body: request }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
