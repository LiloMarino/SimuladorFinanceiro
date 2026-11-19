import { useMutation, useQueryClient } from "@tanstack/react-query";
import { fundKeys } from "@/shared/hooks/fund-keys";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { SetStrategyRequest } from "@/types";

/** Liga, troca, ajusta ou desliga (key nula) a estratégia da carteira da gestora. */
export function useSetFundStrategy(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: SetStrategyRequest) => apiFetch(`/api/funds/${fundId}/strategy`, { method: "PUT", body }),
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.variableIncome() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() }),
      ]),
    onError: (err) => toastApiError(err),
  });
}
