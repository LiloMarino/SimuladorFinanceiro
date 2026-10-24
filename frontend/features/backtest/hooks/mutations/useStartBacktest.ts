import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { BacktestConfigRequest, BacktestStatus } from "@/types";

/** Grava e inicia o backtest; o erro fica com a tela de configuração, que o mostra no lugar do botão. */
export function useStartBacktest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: BacktestConfigRequest) =>
      apiFetch<BacktestStatus>("/api/backtest", { method: "POST", body: config }),
    onSuccess: (status) => {
      queryClient.setQueryData(queryKeys.backtestStatus(), status);
      void queryClient.invalidateQueries({ queryKey: queryKeys.simulationList() });
    },
  });
}
