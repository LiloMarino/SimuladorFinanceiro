import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { CreditOverview } from "@/types";

/** Dívida, nota de risco, oferta, empréstimos e histórico da conta ativa: a pessoal ou a da gestora. */
export function useCredit({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();
  const { accountKey } = useActiveAccount();

  // Multa e mora crescem a cada dia: com parcela em atraso, a cada dia o servidor recalcula o valor
  useRealtime("simulation_update", () => {
    const overview = queryClient.getQueryData<CreditOverview>(queryKeys.creditOverview(accountKey));
    if (overview?.loans.some((loan) => loan.overdue.length > 0)) {
      void queryClient.invalidateQueries({ queryKey: queryKeys.creditOverview(accountKey) });
    }
  });

  return useQuery({
    queryKey: queryKeys.creditOverview(accountKey),
    queryFn: ({ signal }) => apiFetch<CreditOverview>("/api/credit", { signal, activeAccount: true }),
    enabled,
  });
}
