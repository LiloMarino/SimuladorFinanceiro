import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { BacktestSetup } from "@/types";

/** A cobertura do mercado e a configuração de partida: a do backtest `from` (rodar de novo) ou a do mais recente. */
export function useBacktestSetup(from?: number) {
  return useQuery({
    queryKey: queryKeys.backtestSetup(from),
    queryFn: ({ signal }) =>
      apiFetch<BacktestSetup>(`/api/backtest/setup${from === undefined ? "" : `?from=${from}`}`, { signal }),
    // O nome livre e a última configuração mudam a cada backtest: cada abertura pede de novo
    staleTime: 0,
    gcTime: 0,
  });
}
