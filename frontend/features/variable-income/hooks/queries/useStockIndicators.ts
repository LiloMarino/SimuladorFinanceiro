import { keepPreviousData, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { IndicatorSettings, IndicatorsRequest, TechnicalIndicators } from "@/types";

/**
 * Séries dos indicadores ligados e o Resumo técnico, recalculados a cada pregão.
 * O volume vem do próprio histórico do preço, então não entra no pedido.
 */
export function useStockIndicators(ticker: string, settings: IndicatorSettings) {
  const queryClient = useQueryClient();
  const request: IndicatorsRequest = {
    params: settings.params,
    series: settings.visible.filter((key) => key !== "volume"),
  };

  useRealtime(`stock_update:${ticker}`, () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.stockIndicators(ticker) });
  });

  return useQuery({
    queryKey: queryKeys.stockIndicators(ticker, request),
    queryFn: ({ signal }) =>
      apiFetch<TechnicalIndicators>(`/api/variable-income/${ticker}/indicators`, {
        method: "POST",
        body: request,
        signal,
      }),
    // Trocar um parâmetro mantém o desenho anterior até o novo chegar
    placeholderData: keepPreviousData,
  });
}
