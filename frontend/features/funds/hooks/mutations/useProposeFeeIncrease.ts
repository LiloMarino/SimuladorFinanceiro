import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundAssemblyFeeProposalRequest } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** O gestor leva à votação dos cotistas as taxas novas, quando alguma sobe. */
export function useProposeFeeIncrease(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: FundAssemblyFeeProposalRequest) =>
      apiFetch<void>(`/api/funds/${fundId}/assembly/fee-increase`, { method: "POST", body: request }),
    onSettled: () => void queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
