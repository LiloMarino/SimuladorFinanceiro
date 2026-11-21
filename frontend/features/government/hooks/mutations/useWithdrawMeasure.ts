import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useWithdrawMeasure() {
  return useMutation({
    mutationFn: (measureId: number) => apiFetch(`/api/government/measures/${measureId}`, { method: "DELETE" }),
    onError: (err) => toastApiError(err),
  });
}
