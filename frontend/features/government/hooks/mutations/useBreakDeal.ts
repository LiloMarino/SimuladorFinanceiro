import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

/** O presidente rompe o acordo: a emenda para na hora. */
export function useBreakDeal() {
  return useMutation({
    mutationFn: (dealId: number) => apiFetch(`/api/government/deals/${dealId}/break`, { method: "POST" }),
    onError: (err) => toastApiError(err),
  });
}
