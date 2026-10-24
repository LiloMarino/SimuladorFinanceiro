import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { BacktestResult } from "@/types";

/** O backtest salvo: a configuração, onde parou e a série de referência do relatório. */
export function useBacktestResult(simulationId: number, { enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: queryKeys.backtestResult(simulationId),
    queryFn: ({ signal }) => apiFetch<BacktestResult>(`/api/backtest/${simulationId}`, { signal }),
    enabled,
  });
}
