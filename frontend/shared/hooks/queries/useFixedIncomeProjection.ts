import { keepPreviousData, useQuery, useQueryClient } from "@tanstack/react-query";
import { useDebounce } from "use-debounce";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { eventAccountKey } from "@/shared/lib/active-account";
import { queryKeys } from "@/shared/lib/queryKeys";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { FixedIncomeQuote } from "@/types";
import { useRealtime } from "@/shared/hooks/useRealtime";

/**
 * Cotação da boleta (projeção até o vencimento, caixa e tabela do IR) para o valor digitado. O servidor
 * guarda o último valor pedido e entrega a cotação recalculada por `fixed_income_projection:{id}` a cada
 * dia e a cada mudança do caixa da conta.
 */
export function useFixedIncomeProjection(id: string, amount: string) {
  const [debouncedAmount] = useDebounce(amount || "0", 300);
  const client = useQueryClient();
  const { accountKey } = useActiveAccount();
  const queryKey = queryKeys.fixedIncomeProjection(id, debouncedAmount);

  useRealtime(`fixed_income_projection:${id}`, (event) => {
    const sameRequest =
      Number(event.amount) === Number(debouncedAmount) && eventAccountKey(event.account) === accountKey;
    if (sameRequest) void applyRealtime<FixedIncomeQuote>(client, queryKey, event.quote);
  });

  return useQuery({
    queryKey,
    queryFn: ({ signal }) =>
      apiFetch<FixedIncomeQuote>(`/api/fixed-income/${id}/projection?amount=${encodeURIComponent(debouncedAmount)}`, {
        signal,
        activeAccount: true,
      }),
    placeholderData: keepPreviousData,
    staleTime: 0,
  });
}
