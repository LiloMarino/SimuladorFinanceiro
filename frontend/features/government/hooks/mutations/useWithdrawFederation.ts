import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { useRenewElection } from "./useRenewElection";

/** O fundador retira a proposta de federação antes da resposta. */
export function useWithdrawFederation() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: () => apiFetch("/api/government/federations/proposal", { method: "DELETE" }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
