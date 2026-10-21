import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useCancelFutureRecording() {
  return useMutation({
    mutationFn: () => apiFetch("/api/import-assets/future/cancel", { method: "POST" }),
    onError: (err) => toastApiError(err),
  });
}
