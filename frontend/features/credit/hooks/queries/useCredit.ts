import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { CreditOverview } from "@/types";

/** Dívida, nota de risco, oferta, empréstimos e histórico do jogador. */
export function useCredit() {
  const queryClient = useQueryClient();

  // Multa e mora crescem a cada dia: com parcela em atraso, a cada dia o servidor recalcula o valor
  useRealtime("simulation_update", () => {
    const overview = queryClient.getQueryData<CreditOverview>(queryKeys.creditOverview());
    if (overview?.loans.some((loan) => loan.overdue.length > 0)) {
      void queryClient.invalidateQueries({ queryKey: queryKeys.creditOverview() });
    }
  });

  return useQuery({
    queryKey: queryKeys.creditOverview(),
    queryFn: ({ signal }) => apiFetch<CreditOverview>("/api/credit", { signal }),
  });
}
