import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StrategyParamValue, StrategyViewData } from "@/types";

/**
 * O ranking ou a alocação da estratégia sobre a carteira do jogador, com os parâmetros ainda
 * em rascunho: o servidor valida campo a campo e calcula no dia da partida, que faz parte da chave.
 * O bloco anterior fica na tela enquanto o novo chega.
 */
export function useStrategyView(
  key: string,
  params: Record<string, StrategyParamValue> | null,
  currentDate: string | undefined,
) {
  return useQuery({
    queryKey: queryKeys.strategyView(key, params ?? {}, currentDate),
    queryFn: ({ signal }) =>
      apiFetch<StrategyViewData>(`/api/strategies/${key}/view`, { method: "POST", body: { params }, signal }),
    enabled: params !== null,
    placeholderData: keepPreviousData,
  });
}
