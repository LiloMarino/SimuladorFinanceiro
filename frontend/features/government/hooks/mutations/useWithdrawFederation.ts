import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

/** O fundador retira a proposta de federação antes da resposta. */
export function useWithdrawFederation() {
  return useMutation({
    mutationFn: () => apiFetch("/api/government/federations/proposal", { method: "DELETE" }),
    onError: (err) => toastApiError(err),
  });
}
