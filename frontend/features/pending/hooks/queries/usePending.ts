import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { Pending } from "@/types";

/**
 * O que pede ação do jogador agora, das graves para as de aviso. A lista é o estado do
 * servidor: cada evento que cria ou resolve uma pendência manda conferi-la de novo.
 */
export function usePending() {
  const queryClient = useQueryClient();
  const renew = () => void queryClient.invalidateQueries({ queryKey: queryKeys.pending() });

  useRealtime("cash_update", renew);
  useRealtime("credit_installment_late", renew);
  useRealtime("credit_installment_warning", renew);
  useRealtime("credit_installment_paid", renew);
  useRealtime("credit_loan_paid_off", renew);
  useRealtime("strategy_update", renew);
  useRealtime("government_update", renew);

  return useQuery({
    queryKey: queryKeys.pending(),
    queryFn: ({ signal }) => apiFetch<Pending[]>("/api/pending", { signal }),
  });
}
