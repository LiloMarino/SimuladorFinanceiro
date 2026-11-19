import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { fundKeys } from "@/shared/hooks/fund-keys";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { StrategyParamValue, StrategyViewData } from "@/types";

/**
 * O ranking ou a alocação da estratégia sobre a carteira da gestora, com os parâmetros ainda em
 * rascunho; o dia da partida faz parte da chave e o bloco anterior fica na tela enquanto o novo chega.
 */
export function useFundStrategyView(
  fundId: number,
  key: string,
  params: Record<string, StrategyParamValue> | null,
  currentDate: string | undefined,
) {
  return useQuery({
    queryKey: fundKeys.strategyView(fundId, key, params ?? {}, currentDate),
    queryFn: ({ signal }) =>
      apiFetch<StrategyViewData>(`/api/funds/${fundId}/strategy/${key}/view`, {
        method: "POST",
        body: { params },
        signal,
      }),
    enabled: params !== null,
    placeholderData: keepPreviousData,
  });
}
