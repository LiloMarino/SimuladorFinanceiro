import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useReproposeMeasure() {
  return useMutation({
    mutationFn: (measureId: number) => apiFetch(`/api/government/measures/${measureId}/repropose`, { method: "POST" }),
    onError: (err) => toastApiError(err),
  });
}
