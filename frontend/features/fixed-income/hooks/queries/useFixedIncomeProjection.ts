import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useDebounce } from "use-debounce";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FixedIncomeQuote } from "@/types";

/**
 * Cotação da boleta (projeção até o vencimento, caixa e tabela do IR) para o valor digitado. A chave
 * inclui a data da simulação, então a projeção acompanha o avanço dos dias.
 */
export function useFixedIncomeProjection(id: string, amount: string, currentDate: string) {
  const [debouncedAmount] = useDebounce(amount || "0", 300);

  return useQuery({
    queryKey: queryKeys.fixedIncomeProjection(id, debouncedAmount, currentDate),
    queryFn: ({ signal }) =>
      apiFetch<FixedIncomeQuote>(`/api/fixed-income/${id}/projection?amount=${encodeURIComponent(debouncedAmount)}`, {
        signal,
      }),
    placeholderData: keepPreviousData,
  });
}
