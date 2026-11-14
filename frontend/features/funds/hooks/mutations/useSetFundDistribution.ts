import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundDistributionRequest, FundSummary } from "@/types";
import { fundKeys } from "../fund-keys";

/** Muda a parte do lucro distribuída: a nova fica pendente e vale no primeiro dia útil do mês seguinte. */
export function useSetFundDistribution(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: FundDistributionRequest) =>
      apiFetch<FundSummary>(`/api/funds/${fundId}/distribution`, { method: "PUT", body: request }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
