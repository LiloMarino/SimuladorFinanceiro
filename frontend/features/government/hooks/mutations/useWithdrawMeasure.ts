import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { useRenewElection } from "./useRenewElection";

export function useWithdrawMeasure() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (measureId: number) => apiFetch(`/api/government/measures/${measureId}`, { method: "DELETE" }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
