import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StrategyParamValue, StrategySignal } from "@/types";

/**
 * O que a estratégia olha numa ação, com os parâmetros ainda em rascunho: o servidor valida
 * campo a campo e devolve as linhas. O gráfico anterior fica na tela enquanto o novo chega.
 */
export function useStrategySignal(key: string, ticker: string | null, params: Record<string, StrategyParamValue>) {
  return useQuery({
    queryKey: queryKeys.strategySignal(key, ticker ?? "", params),
    queryFn: ({ signal }) =>
      apiFetch<StrategySignal>(`/api/strategies/${key}/signal`, { method: "POST", body: { params, ticker }, signal }),
    enabled: ticker !== null,
    placeholderData: keepPreviousData,
  });
}
