import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { applyStocksUpdate } from "@/shared/lib/market-quotes";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtimeDelta } from "@/shared/lib/realtime/apply-realtime";
import type { MarketQuote } from "@/types";

/**
 * Lista de mercado, mantida viva via stocks_update. O evento traz só a cotação do
 * dia: o mini gráfico e o setor vêm da busca. Ticker que a lista ainda não tem (uma
 * cota recém-listada) renova a busca.
 */
export function useVariableIncomeStocks() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.variableIncomeList(),
    queryFn: ({ signal }) => apiFetch<MarketQuote[]>("/api/variable-income", { signal }),
  });

  useRealtime("stocks_update", ({ stocks }) => {
    // Um ticker que a lista ainda não tem manda ler a lista de novo
    void applyRealtimeDelta<MarketQuote[]>(queryClient, queryKeys.variableIncomeList(), (previous) => {
      const { quotes, hasUnknown } = applyStocksUpdate(previous, stocks);
      return hasUnknown ? null : quotes;
    });
  });

  return query;
}
