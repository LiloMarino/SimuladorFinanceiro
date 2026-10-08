import { keepPreviousData } from "@tanstack/react-query";
import { useDebounce } from "use-debounce";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FixedIncomeProjection } from "@/types";

/**
 * Projeção até o vencimento calculada pelo backend para o valor digitado. A chave
 * inclui a data da simulação, então a projeção acompanha o avanço dos dias.
 */
export function useFixedIncomeProjection(id: string, amount: string, currentDate: string) {
  const [debouncedAmount] = useDebounce(amount || "0", 300);

  return useApiQuery({
    queryKey: queryKeys.fixedIncomeProjection(id, debouncedAmount, currentDate),
    queryFn: ({ signal }) =>
      apiFetch<FixedIncomeProjection>(
        `/api/fixed-income/${id}/projection?amount=${encodeURIComponent(debouncedAmount)}`,
        { signal },
      ),
    placeholderData: keepPreviousData,
  });
}
