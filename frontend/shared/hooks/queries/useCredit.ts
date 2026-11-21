import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { eventAccountKey } from "@/shared/lib/active-account";
import { queryKeys } from "@/shared/lib/queryKeys";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { CreditOverview } from "@/types";

/** Dívida, nota de risco, oferta, empréstimos e histórico da conta ativa: a pessoal ou a da gestora. */
export function useCredit({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();
  const { accountKey } = useActiveAccount();

  // Multa e mora crescem a cada dia: o servidor entrega o crédito de cada conta com parcela em atraso por `credit_update`
  useRealtime(
    "credit_update",
    ({ overview, account }) => {
      if (eventAccountKey(account) !== accountKey) return;
      void applyRealtime<CreditOverview>(queryClient, queryKeys.creditOverview(accountKey), overview);
    },
    enabled,
  );

  return useQuery({
    queryKey: queryKeys.creditOverview(accountKey),
    queryFn: ({ signal }) => apiFetch<CreditOverview>("/api/credit", { signal, activeAccount: true }),
    staleTime: 0,
    enabled,
  });
}
