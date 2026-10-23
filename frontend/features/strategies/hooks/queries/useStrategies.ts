import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StrategyInfo } from "@/types";

/** As estratégias do app, com regra, parâmetros, faixa e padrão da partida. */
export function useStrategies() {
  return useQuery({
    queryKey: queryKeys.strategyList(),
    queryFn: ({ signal }) => apiFetch<StrategyInfo[]>("/api/strategies", { signal }),
  });
}
