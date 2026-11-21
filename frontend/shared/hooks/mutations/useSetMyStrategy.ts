import { useMutation, useQueryClient } from "@tanstack/react-query";
import { fundKeys } from "@/shared/hooks/fund-keys";
import { useStrategyRoute } from "@/shared/hooks/useStrategyRoute";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { strategyFundId, strategyPaths } from "@/shared/lib/strategy-route";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { SetStrategyRequest } from "@/types";

/** Liga, troca, ajusta ou desliga (key nula) a estratégia da conta do topo; ligar, trocar e desligar cancelam as ordens abertas dela. */
export function useSetMyStrategy() {
  const queryClient = useQueryClient();
  const fundId = strategyFundId(useStrategyRoute());

  return useMutation({
    mutationFn: (body: SetStrategyRequest) => apiFetch(strategyPaths(fundId).mine, { method: "PUT", body }),
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.strategies() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.variableIncome() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.savedStrategyParams() }),
        ...(fundId === null ? [] : [queryClient.invalidateQueries({ queryKey: fundKeys.all() })]),
      ]),
    onError: (err) => toastApiError(err),
  });
}
