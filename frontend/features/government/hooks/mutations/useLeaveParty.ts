import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { useRenewElection } from "./useRenewElection";

export function useLeaveParty() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: () => apiFetch("/api/government/membership", { method: "DELETE" }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
