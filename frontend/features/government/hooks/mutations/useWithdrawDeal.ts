import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { useRenewBase } from "./useRenewBase";

/** O presidente cancela a proposta antes da resposta. */
export function useWithdrawDeal() {
  const renew = useRenewBase();

  return useMutation({
    mutationFn: (dealId: number) => apiFetch(`/api/government/deals/${dealId}`, { method: "DELETE" }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
