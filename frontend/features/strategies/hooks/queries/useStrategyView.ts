import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useStrategyRoute } from "@/shared/hooks/useStrategyRoute";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { strategyFundId, strategyPaths } from "@/shared/lib/strategy-route";
import type { StrategyParamValue, StrategyViewData } from "@/types";

/**
 * O ranking ou a alocação da estratégia sobre a carteira da conta do topo, com os parâmetros ainda
 * em rascunho: o servidor valida campo a campo e calcula no dia da partida, que faz parte da chave.
 * O bloco anterior fica na tela enquanto o novo chega.
 */
export function useStrategyView(
  key: string,
  params: Record<string, StrategyParamValue> | null,
  currentDate: string | undefined,
) {
  const fundId = strategyFundId(useStrategyRoute());

  return useQuery({
    queryKey: queryKeys.strategyView(fundId ?? "personal", key, params ?? {}, currentDate),
    queryFn: ({ signal }) =>
      apiFetch<StrategyViewData>(strategyPaths(fundId).view(key), { method: "POST", body: { params }, signal }),
    enabled: params !== null,
    placeholderData: keepPreviousData,
  });
}
