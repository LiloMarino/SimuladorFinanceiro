import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { PrepaymentPreview } from "@/types";

/** As duas formas de amortizar, a quitação e o caixa, para o valor digitado; a data do dia entra na chave. */
export function usePrepaymentPreview(loanId: string, amount: string, currentDate: string) {
  const { accountKey } = useActiveAccount();

  return useQuery({
    queryKey: queryKeys.prepaymentPreview(accountKey, loanId, amount, currentDate),
    queryFn: ({ signal }) =>
      apiFetch<PrepaymentPreview>(`/api/credit/loans/${loanId}/prepayment?amount=${amount}`, {
        signal,
        activeAccount: true,
      }),
    placeholderData: keepPreviousData,
  });
}
