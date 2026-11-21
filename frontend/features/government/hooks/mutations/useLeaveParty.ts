import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useLeaveParty() {
  return useMutation({
    mutationFn: () => apiFetch("/api/government/membership", { method: "DELETE" }),
    onError: (err) => toastApiError(err),
  });
}
