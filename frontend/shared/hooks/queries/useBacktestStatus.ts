import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { BacktestStatus } from "@/types";
import { applyProgress, EMPTY_STATUS } from "@/shared/lib/backtest-progress";

/** O andamento do backtest que roda (vazio quando não há): a consulta mais os avisos de cada 20 pregões. */
export function useBacktestStatus() {
  const queryClient = useQueryClient();

  useRealtime("backtest_started", (status) => {
    queryClient.setQueryData(queryKeys.backtestStatus(), status);
  });
  useRealtime("backtest_progress", (event) => {
    const current = queryClient.getQueryData<BacktestStatus>(queryKeys.backtestStatus());
    // Sem o início guardado (aba aberta no meio), a consulta traz o estado inteiro
    if (!current?.progress) void queryClient.invalidateQueries({ queryKey: queryKeys.backtestStatus() });
    else queryClient.setQueryData(queryKeys.backtestStatus(), applyProgress(current, event));
  });
  useRealtime("backtest_ended", () => {
    queryClient.setQueryData(queryKeys.backtestStatus(), EMPTY_STATUS);
    void queryClient.invalidateQueries({ queryKey: queryKeys.simulationList() });
  });

  return useQuery({
    queryKey: queryKeys.backtestStatus(),
    queryFn: ({ signal }) => apiFetch<BacktestStatus>("/api/backtest/status", { signal }),
  });
}
