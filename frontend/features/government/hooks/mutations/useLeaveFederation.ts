import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { useRenewElection } from "./useRenewElection";

/** O fundador tira o partido da federação: ela se desfaz na hora para os dois. */
export function useLeaveFederation() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: () => apiFetch("/api/government/federations", { method: "DELETE" }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
