import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useDebounce } from "use-debounce";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FixedIncomeRedemptionQuote } from "@/types";

/**
 * Cotação do resgate (bruto, IOF, IR e líquido) para o valor que o jogador quer receber no caixa. A chave
 * inclui a data da simulação, então o cálculo acompanha o avanço dos dias.
 */
export function useFixedIncomeRedemption(id: string, amount: string, currentDate: string, enabled: boolean) {
  const [debouncedAmount] = useDebounce(amount || "0", 300);

  return useQuery({
    queryKey: queryKeys.fixedIncomeRedemption(id, debouncedAmount, currentDate),
    queryFn: ({ signal }) =>
      apiFetch<FixedIncomeRedemptionQuote>(
        `/api/fixed-income/${id}/redemption?amount=${encodeURIComponent(debouncedAmount)}`,
        { signal },
      ),
    enabled,
    placeholderData: keepPreviousData,
  });
}
