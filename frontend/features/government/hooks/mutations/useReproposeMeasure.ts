import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { useRenewElection } from "./useRenewElection";

export function useReproposeMeasure() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (measureId: number) => apiFetch(`/api/government/measures/${measureId}/repropose`, { method: "POST" }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
