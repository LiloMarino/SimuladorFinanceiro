import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { applyStocksUpdate } from "@/shared/lib/market-quotes";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
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
    const previous = queryClient.getQueryData<MarketQuote[]>(queryKeys.variableIncomeList());
    if (!previous) return;
    const { quotes, hasUnknown } = applyStocksUpdate(previous, stocks);
    queryClient.setQueryData(queryKeys.variableIncomeList(), quotes);
    if (hasUnknown) {
      void queryClient.invalidateQueries({ queryKey: queryKeys.variableIncomeList() }, { cancelRefetch: false });
    }
  });

  return query;
}
