import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { Stock } from "@/types";

/**
 * Lista de ações da renda variável, mantida viva via stocks_update.
 * Consumida por variable-income.tsx e portfolio.tsx — compartilham a mesma
 * busca e a mesma assinatura WS (dedup por queryKey).
 */
export function useVariableIncomeStocks() {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.variableIncomeList(),
    queryFn: ({ signal }) => apiFetch<Stock[]>("/api/variable-income", { signal }),
  });

  useRealtime("stocks_update", (data) => {
    queryClient.setQueryData(queryKeys.variableIncomeList(), data.stocks);
  });

  return query;
}
