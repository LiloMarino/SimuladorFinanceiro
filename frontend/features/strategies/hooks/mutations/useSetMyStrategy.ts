import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { SetStrategyRequest } from "@/types";

/** Liga, troca, ajusta ou desliga (key nula) a estratégia; ligar, trocar e desligar cancelam as ordens abertas. */
export function useSetMyStrategy() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: SetStrategyRequest) => apiFetch("/api/strategies/me", { method: "PUT", body }),
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.strategies() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.variableIncome() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() }),
      ]),
    onError: (err) => toastApiError(err),
  });
}
