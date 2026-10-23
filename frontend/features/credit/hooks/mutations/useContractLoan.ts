import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { ContractLoanRequest } from "@/types";
import { useRenewCredit } from "./useRenewCredit";

export function useContractLoan() {
  const renew = useRenewCredit();

  return useMutation({
    mutationFn: (body: ContractLoanRequest) => apiFetch("/api/credit/loans", { method: "POST", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
