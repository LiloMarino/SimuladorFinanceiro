import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundBuybackRequest } from "@/types";
import { fundKeys } from "../fund-keys";

/** Abre a recompra: uma ordem de compra da gestora, paga com o caixa dela, que queima as cotas compradas. */
export function useOpenFundBuyback(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: FundBuybackRequest) =>
      apiFetch<void>(`/api/funds/${fundId}/buyback`, { method: "POST", body: request }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
