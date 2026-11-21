import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

/** O presidente cancela a proposta antes da resposta. */
export function useWithdrawDeal() {
  return useMutation({
    mutationFn: (dealId: number) => apiFetch(`/api/government/deals/${dealId}`, { method: "DELETE" }),
    onError: (err) => toastApiError(err),
  });
}
