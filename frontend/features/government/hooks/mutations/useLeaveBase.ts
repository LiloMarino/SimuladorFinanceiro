import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { useRenewBase } from "./useRenewBase";

/** O líder do partido aliado sai da base do governo: a emenda para na hora. */
export function useLeaveBase() {
  const renew = useRenewBase();

  return useMutation({
    mutationFn: () => apiFetch("/api/government/deals/leave", { method: "POST" }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
