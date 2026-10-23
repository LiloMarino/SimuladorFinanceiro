import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { useRenewCredit } from "./useRenewCredit";

export function usePayOverdue(loanId: string) {
  const renew = useRenewCredit();

  return useMutation({
    mutationFn: () => apiFetch(`/api/credit/loans/${loanId}/overdue`, { method: "POST" }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
