import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FundAccount } from "@/types";

/** As contas com que o jogador opera: a pessoal primeiro e depois cada gestora que ele gere. Só existe com a expansão Gestoras ligada. */
export function useFundAccounts({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  // Cada movimento de caixa chega marcado com a conta: o caixa dela se atualiza na lista
  useRealtime(
    "cash_update",
    ({ cash, account }) => {
      queryClient.setQueryData<FundAccount[]>(queryKeys.fundAccounts(), (accounts) =>
        accounts?.map((item) => (item.fund_id === account ? { ...item, cash } : item)),
      );
    },
    enabled,
  );

  return useQuery({
    queryKey: queryKeys.fundAccounts(),
    queryFn: ({ signal }) => apiFetch<FundAccount[]>("/api/funds/accounts", { signal }),
    enabled,
  });
}
