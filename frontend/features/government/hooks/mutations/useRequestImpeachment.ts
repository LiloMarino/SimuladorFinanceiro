import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

/** O líder do partido abre o pedido de impeachment contra o presidente. */
export function useRequestImpeachment() {
  return useMutation({
    mutationFn: () => apiFetch("/api/government/congress/impeachment", { method: "POST" }),
    onError: (err) => toastApiError(err),
  });
}
