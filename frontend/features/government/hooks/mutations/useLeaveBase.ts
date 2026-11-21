import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

/** O líder do partido aliado sai da base do governo: a emenda para na hora. */
export function useLeaveBase() {
  return useMutation({
    mutationFn: () => apiFetch("/api/government/deals/leave", { method: "POST" }),
    onError: (err) => toastApiError(err),
  });
}
