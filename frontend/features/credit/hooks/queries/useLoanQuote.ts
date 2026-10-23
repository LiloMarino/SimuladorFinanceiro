import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { LoanQuote } from "@/types";

/** Simulação do empréstimo: parcela, juro, cronograma e a nota projetada. O valor vai em reais, como texto. */
export function useLoanQuote(amount: string, termMonths: number, { enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: queryKeys.loanQuote(amount, termMonths),
    queryFn: ({ signal }) =>
      apiFetch<LoanQuote>(`/api/credit/quote?amount=${amount}&term_months=${termMonths}`, { signal }),
    enabled,
    placeholderData: keepPreviousData,
  });
}
