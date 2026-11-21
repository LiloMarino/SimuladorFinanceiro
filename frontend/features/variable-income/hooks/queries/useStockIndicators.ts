import { hashKey, keepPreviousData, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtimeDelta } from "@/shared/lib/realtime/apply-realtime";
import type { IndicatorSettings, IndicatorsRequest, TechnicalIndicators } from "@/types";
import { mergeIndicatorsUpdate } from "../../lib/asset-feed";

/**
 * Séries dos indicadores ligados e o Resumo técnico. O servidor guarda o último pedido e a cada
 * pregão entrega o ponto novo de cada série e o resumo por `indicators_update:{ticker}`.
 * O volume vem do próprio histórico do preço, então não entra no pedido.
 */
export function useStockIndicators(ticker: string, settings: IndicatorSettings) {
  const queryClient = useQueryClient();
  const request: IndicatorsRequest = {
    params: settings.params,
    series: settings.visible.filter((key) => key !== "volume"),
  };
  const queryKey = queryKeys.stockIndicators(ticker, request);

  useRealtime(`indicators_update:${ticker}`, (event) => {
    // O aviso é do pedido que o servidor guardou: um pedido já trocado na tela não o recebe
    if (hashKey([event.request]) !== hashKey([request])) return;
    void applyRealtimeDelta<TechnicalIndicators>(queryClient, queryKey, (current) =>
      mergeIndicatorsUpdate(current, event),
    );
  });

  return useQuery({
    queryKey,
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
