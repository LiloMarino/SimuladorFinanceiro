import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { PayrollQuote } from "@/types";

/** Simulação do consignado: parcela, juro travado, margem livre depois e o máximo por prazo. O dia da partida entra na chave. */
export function usePayrollQuote(
  amount: string,
  termMonths: number,
  currentDate: string,
  { enabled = true }: { enabled?: boolean } = {},
) {
  const { accountKey } = useActiveAccount();

  return useQuery({
    queryKey: queryKeys.payrollQuote(accountKey, amount, termMonths, currentDate),
    queryFn: ({ signal }) =>
      apiFetch<PayrollQuote>(`/api/credit/payroll/quote?amount=${amount}&term_months=${termMonths}`, {
        signal,
        activeAccount: true,
      }),
    enabled,
    placeholderData: keepPreviousData,
  });
}
