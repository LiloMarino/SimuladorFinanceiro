import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { PrepayLoanRequest } from "@/types";
import { useRenewCredit } from "./useRenewCredit";

export function usePrepayLoan(loanId: string) {
  const renew = useRenewCredit();

  return useMutation({
    mutationFn: (body: PrepayLoanRequest) =>
      apiFetch(`/api/credit/loans/${loanId}/prepayment`, { method: "POST", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
