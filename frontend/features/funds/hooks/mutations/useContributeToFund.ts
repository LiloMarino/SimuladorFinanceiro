import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundContributionRequest, FundContributionResponse } from "@/types";
import { fundKeys } from "../fund-keys";

/** Leva caixa e ações da carteira do gestor para a gestora, em troca de cotas. */
export function useContributeToFund() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ fundId, request }: { fundId: number; request: FundContributionRequest }) =>
      apiFetch<FundContributionResponse>(`/api/funds/${fundId}/contributions`, { method: "POST", body: request }),
    onSettled: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.variableIncome() }),
      ]),
    onError: (err) => toastApiError(err),
  });
}
