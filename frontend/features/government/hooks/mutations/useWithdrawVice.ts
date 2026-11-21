import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

/** O fundador retira o convite de vice (aguardando, aceito ou recusado). */
export function useWithdrawVice() {
  return useMutation({
    mutationFn: () => apiFetch("/api/government/parties/vice", { method: "DELETE" }),
    onError: (err) => toastApiError(err),
  });
}
